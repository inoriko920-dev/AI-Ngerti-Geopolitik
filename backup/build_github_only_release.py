#!/usr/bin/env python3
"""Produce a self-contained GITHUB-ONLY verified repository recovery ZIP.
Only source project content fetched from GitHub is included, with generated verification metadata.
"""
import collections, csv, datetime, hashlib, io, os, pathlib, re, shutil, subprocess, tempfile, zipfile
from zoneinfo import ZoneInfo

REPO="inoriko920-dev/AI-Ngerti-Geopolitik"
URL="https://github.com/"+REPO+".git"
ROOT=pathlib.Path.cwd()
OUT=ROOT/"backup-release-output"
OUT.mkdir(exist_ok=True)
WORK=ROOT/"backup-release-work"
if WORK.exists(): shutil.rmtree(WORK)
WORK.mkdir()
MIRROR=WORK/"repo.git"
def run(*args,check=True):
    return subprocess.run(args,check=check,capture_output=True)
def git(*args):
    return run("git","-C",str(MIRROR),*args).stdout
def txt(*args): return git(*args).decode("utf-8",errors="replace")
def put(root,rel,data):
    p=root/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(data if isinstance(data,bytes) else data.encode("utf-8"))
    return p
def sha(path):
    with open(path,"rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()

run("git","clone","--mirror",URL,str(MIRROR))
run("git","-C",str(MIRROR),"fsck","--full","--no-reflogs")
refs=txt("for-each-ref","--format=%(refname) %(objectname)").splitlines()
heads=[s for s in refs if s.startswith("refs/heads/")]
tags=[s for s in refs if s.startswith("refs/tags/")]
pulls=[s for s in refs if s.startswith("refs/pull/")]
main_sha=txt("rev-parse","refs/heads/main").strip()
timestamp=datetime.datetime.now(ZoneInfo("Asia/Jakarta"))
stamp=timestamp.strftime("%Y-%m-%d_%H-%M-%S-WIB")
dest=WORK/"AI-Ngerti-Geopolitik"
dest.mkdir()
bundle=dest/"GIT"/"AI-Ngerti-Geopolitik-COMPLETE-GIT-HISTORY.bundle"
bundle.parent.mkdir()
run("git","-C",str(MIRROR),"bundle","create",str(bundle),"--all")
verify=run("git","-C",str(MIRROR),"bundle","verify",str(bundle))
put(dest,"GIT_BUNDLE_VERIFY.txt",verify.stdout+verify.stderr)
run("git","-C",str(MIRROR),"bundle","list-heads",str(bundle))
# Verify independently by locally cloning the bundle and checking every Git object.
recovery=WORK/"test-restored.git"
run("git","clone","--mirror",str(bundle),str(recovery))
run("git","-C",str(recovery),"fsck","--full","--no-reflogs")
assert run("git","-C",str(recovery),"rev-parse","refs/heads/main").stdout.decode().strip()==main_sha
src=dest/"SOURCE"/"AI-Ngerti-Geopolitik-SOURCE-MAIN.zip"
src.parent.mkdir()
run("git","-C",str(MIRROR),"archive","--format=zip","--output="+str(src),"refs/heads/main")

main_files={}
bad_docx=[]
with zipfile.ZipFile(src) as archive:
    assert archive.testzip() is None
    for info in archive.infolist():
        if info.is_dir(): continue
        path=info.filename
        main_files[path]=(info.file_size,info.CRC)
        if path.startswith("docs/") or path in ("AGENTS.md","HANDOFF.md","README.md","THIRD_PARTY_NOTICES.md"):
            b=archive.read(info)
            put(dest,"GITHUB_MAIN_DOCUMENTATION/"+path,b)
            if path.lower().endswith(".docx"):
                try:
                    with zipfile.ZipFile(io.BytesIO(b)) as doc:
                        if doc.testzip() or "word/document.xml" not in doc.namelist() or "[Content_Types].xml" not in doc.namelist():
                            bad_docx.append(path)
                except (zipfile.BadZipFile,ValueError):
                    bad_docx.append(path)
ui_count=sum(bool(re.fullmatch(r"docs/ui_reference/raw/UI-\d{3}\.png",p)) for p in main_files)
assert ui_count==42, "UI count unexpected: "+str(ui_count)
main_paths=set(main_files)
variants={}
for refline in heads:
    ref=refline.split()[0]
    for row in git("ls-tree","-r","-l",ref).decode().splitlines():
        h,path=row.split("\t",1)
        typ,kind,oid,size=h.split()
        if kind!="blob" or path in main_paths: continue
        item=variants.setdefault((path,oid),{"branches":[],"size":int(size)})
        item["branches"].append(ref)
branch_csv=io.StringIO()
writer=csv.writer(branch_csv)
writer.writerow(["path_in_repo","git_blob_sha","backup_path","branches"])
for (path,oid),entry in sorted(variants.items()):
    b=git("cat-file","blob",oid)
    assert len(b)==entry["size"]
    pp=pathlib.PurePosixPath(path)
    unique=str(pp.parent/(pp.stem+"__GIT-"+oid[:12]+pp.suffix))
    backup_path="GITHUB_BRANCH_ONLY_FILES/"+unique
    put(dest,backup_path,b)
    writer.writerow([path,oid,backup_path,";".join(entry["branches"])])
put(dest,"GITHUB_BRANCH_ONLY_FILES_INDEX.csv",branch_csv.getvalue())
put(dest,"BRANCHES.txt","\n".join(heads)+"\n")
put(dest,"TAGS.txt","\n".join(tags)+"\n" if tags else "NO_TAGS_FOUND\n")
put(dest,"ALL_GIT_REFS.txt","\n".join(refs)+"\n")
put(dest,"MAIN_COMMIT.txt",main_sha+"\n")
put(dest,"COMMIT_HISTORY.txt",txt("log","--all","--pretty=format:%H | %P | %aI | %an | %s")+"\n")
commit_count=len(set(txt("log","--all","--format=%H").splitlines()))
put(dest,"COMMIT_COUNT.txt",str(commit_count)+"\n")
put(dest,"GIT_FSCK_RESULTS.txt","GitHub clone mirror: PASS\nBundle clone: PASS\nGit fsck --full --no-reflogs: PASS\n")
put(dest,"DOCX_FROM_GITHUB_STATUS.txt",
     "Original GitHub DOCX files remain unchanged; no outside copies were inserted.\n"+
     f"Invalid main branch DOCX count: {len(bad_docx)}\n"+
     "\n".join(bad_docx)+"\n")
brand=re.compile(r"logo|icon|brand|favicon|\.ico$",re.I)
logos=[p for p in main_paths if brand.search(p)]
logos+= [p for p,oid in variants if brand.search(p)]
put(dest,"LOGO_ASSET_STATUS.txt", "Named logo/icon/branding tracked paths: "+str(len(logos))+"\n"+"\n".join(sorted(set(logos)))+"\n")
put(dest,"BUILD/BUILD_NOT_AVAILABLE.txt","No verified stable Windows portable release included. CI test evidence is not a final app build.\n")
# Optional GitHub Actions test artifact from this same repository, not from another source.
ci=WORK/"ci-previous-run"
ci.mkdir()
res=run("gh","run","download","37936886869","--repo",REPO,"--name","ANG-Pilot-A-Real-H264-Windows","--dir",str(ci),check=False)
if res.returncode==0 and list(ci.rglob("*")):
    evidence=dest/"CI_EVIDENCE"/"ANG-Pilot-A-Real-H264-Windows-GITHUB-ACTIONS-ARTIFACT.zip"
    evidence.parent.mkdir()
    with zipfile.ZipFile(evidence,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in ci.rglob("*"):
            if p.is_file():z.write(p,p.relative_to(ci))
    put(dest,"CI_EVIDENCE/README.txt","Downloaded directly from this repo's GitHub Actions run 37936886869. CI test evidence only.\n")
else:
    put(dest,"CI_EVIDENCE/ARTIFACT_UNAVAILABLE.txt","CI workflow artifact was not available for download, but Git bundle/source unaffected.\n")

restore=r'''param([string]$OutputFolder="")
$ErrorActionPreference="Stop"
$repoRoot=Split-Path -Parent $PSScriptRoot
$bundle=Join-Path $repoRoot "GIT\AI-Ngerti-Geopolitik-COMPLETE-GIT-HISTORY.bundle"
if (-not (Get-Command git -ErrorAction SilentlyContinue)){ throw "Install Git for Windows first." }
if (-not $OutputFolder) {$OutputFolder=Join-Path (Split-Path -Parent $repoRoot) "AI-Ngerti-Geopolitik-RESTORED.git"}
if (Test-Path $OutputFolder) {throw "Output location already exists; choose another empty folder."}
git clone --mirror "$bundle" "$OutputFolder"
if ($LASTEXITCODE -ne 0) {throw "Git restore failed."}
git -C "$OutputFolder" fsck --full --no-reflogs
if ($LASTEXITCODE -ne 0) {throw "Restored Git object check failed."}
Write-Host "LOCAL GIT RESTORED. NO PUSH PERFORMED."
Write-Host 'Create an EMPTY GitHub repo, then manually:'
Write-Host ('git -C "'+$OutputFolder+'" remote set-url origin https://github.com/NEW-ACCOUNT/AI-Ngerti-Geopolitik.git')
Write-Host ('git -C "'+$OutputFolder+'" push origin "refs/heads/*:refs/heads/*"')
Write-Host ('git -C "'+$OutputFolder+'" push origin "refs/tags/*:refs/tags/*"')
Write-Host "refs/pull/* kept locally; GitHub restricts push to refs/pull."
'''
put(dest,"RECOVERY/RESTORE_TO_NEW_GITHUB.ps1",restore)
verify_ps=r'''$ErrorActionPreference="Stop"
$root=Split-Path -Parent $PSScriptRoot
$checks=Import-Csv (Join-Path $root "00_SHA256SUMS.csv")
foreach($check in $checks){
    $path=Join-Path $root ($check.Path -replace '/','\')
    if(-not (Test-Path $path -PathType Leaf)){throw "Missing file $path"}
    $h=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if($h -ne $check.SHA256.ToLowerInvariant()){throw "SHA256 FAILED for $path"}
}
Write-Host "SHA256 PASS ($($checks.Count) files)"
if(Get-Command git -ErrorAction SilentlyContinue){
    $scratch=Join-Path $env:TEMP ([guid]::NewGuid().ToString("N"))
    try{
        git init --bare "$scratch" | Out-Null
        git -C "$scratch" bundle verify (Join-Path $root "GIT\AI-Ngerti-Geopolitik-COMPLETE-GIT-HISTORY.bundle")
        if($LASTEXITCODE -ne 0){throw "Git bundle verification failed"}
        Write-Host "Git Bundle PASS"
    } finally {if(Test-Path $scratch){Remove-Item -Force -Recurse $scratch}}
}
'''
put(dest,"RECOVERY/VERIFY_BACKUP.ps1",verify_ps)
put(dest,"VERIFY_ALL_BACKUP.ps1",'& "$PSScriptRoot\\RECOVERY\\VERIFY_BACKUP.ps1"\n')
put(dest,"RESTORE_ALL.ps1",'& "$PSScriptRoot\\RECOVERY\\RESTORE_TO_NEW_GITHUB.ps1"\n')
put(dest,"00_BACKUP_INFO.txt",
    f"Backup created from GitHub only: {timestamp.isoformat()}\nRepo: {REPO}\nDefault main: {main_sha}\n")
put(dest,"00_MASTER_MANIFEST.txt",
    f"REPO: {REPO}\nMAIN_COMMIT: {main_sha}\nBRANCH_REFS: {len(heads)}\nTAG_REFS: {len(tags)}\nPULL_REFS: {len(pulls)}\nUNIQUE_COMMITS: {commit_count}\nUI_PNG: {ui_count}\nBRANCH_EXTRA_FILE_VERSIONS: {len(variants)}\nINVALID_DOCX_IN_ORIGINAL: {len(bad_docx)}\nBUILD: NOT_AVAILABLE\nRESTORE: RECOVERY/RESTORE_TO_NEW_GITHUB.ps1\n")
put(dest,"00_README_PERTAMA.txt",f"""BACKUP FULL AI-NGERTI-GEOPOLITIK - FROM GITHUB ONLY
Date/time WIB: {timestamp.isoformat()}
Main SHA: {main_sha}

INCLUDED:
1) Git Bundle with all {len(heads)} heads and {len(pulls)} PR refs; {commit_count} unique commits
2) Main source snapshot ZIP with all tracked code and resources (including 42 UI PNGs)
3) All tracked documentation, ASTRA/SOL DOCX, prompt and image files from main as directly accessible copies
4) Branch-only distinct files from all GitHub branch tips ({len(variants)} file versions), plus full histories in Git Bundle
5) One Actions-run artifact when available (NOT a stable release/build)
6) SHA256, recovery scripts and manifests for Windows 11.

IMPORTANT:
- No Library copy, local document, external logo, or outside repository is included.
- {len(bad_docx)} DOCX files committed in GitHub main fail validation; these originals remain in the backup without replacement.
- No standalone logo was found by filename if LOGO_ASSET_STATUS.txt lists 0.
- No verified stable Windows build/installer.
- Git bundle does NOT preserve GitHub issue/PR discussions, settings, secrets, or Action run history.
- For recovery, unzip, run VERIFY_ALL_BACKUP.ps1, then RESTORE_ALL.ps1. The latter restores locally and NEVER pushes automatically.
""")
# Checksum every internal file except checksum files themselves, to avoid recursion.
records=[]
for file in sorted(dest.rglob("*")):
    if file.is_file():
        rel=file.relative_to(dest).as_posix()
        if rel not in ("00_SHA256SUMS.csv","00_SHA256SUMS.txt"):
            records.append((rel,file.stat().st_size,sha(file)))
csvs=io.StringIO()
wr=csv.writer(csvs); wr.writerow(["Path","SizeBytes","SHA256"]);wr.writerows(records)
put(dest,"00_SHA256SUMS.csv",csvs.getvalue())
put(dest,"00_SHA256SUMS.txt","\n".join(f"{h}  {p}" for p,n,h in records)+"\n")
out=OUT/("AI-Ngerti-Geopolitik-GITHUB-ONLY-FULL-BACKUP-"+stamp+".zip")
with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=2,allowZip64=True) as archive:
    for p in sorted(dest.rglob("*")):
        if p.is_file():archive.write(p,arcname="AI-Ngerti-Geopolitik/"+p.relative_to(dest).as_posix())
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
    cs=list(csv.DictReader(io.StringIO(archive.read("AI-Ngerti-Geopolitik/00_SHA256SUMS.csv").decode())))
    for r in cs:
        b=archive.read("AI-Ngerti-Geopolitik/"+r["Path"])
        assert len(b)==int(r["SizeBytes"]) and hashlib.sha256(b).hexdigest()==r["SHA256"],"SHA mismatch"
assert len(cs)==len(records)
digest=sha(out)
sha_file=OUT/(out.name+".sha256")
sha_file.write_text(f"{digest}  {out.name}\n",encoding="utf-8")
print("RELEASE_ZIP="+str(out))
print("RELEASE_SHA="+digest)
print("COUNTS",len(heads),len(tags),len(pulls),commit_count,ui_count,len(variants),len(cs))
