# CODE CONSTITUTION — CC-ANG-v1.0

Canonical detail: `docs/planning/08_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_AI_NGERTI_GEOPOLITIK.*`.

1. Search -> Understand -> Modify before creating a new owner/service/helper.
2. One concern has one canonical owner.
3. Domain is pure and independent of Qt/engine/provider/credential/process implementations.
4. Presentation never imports concrete infrastructure adapters.
5. All project mutation goes through semantic CommandBus once command implementation begins.
6. No mutable global product/session state.
7. No blocking network/probe/render/native-engine work on the UI thread.
8. No plaintext secrets, hardcoded developer paths, fake-green tests, or static-image runtime UI.
9. Material architecture exceptions require ADR/Astra review.
