# STAR: A Schema-Guided Dialog Dataset for Transfer Learning

## Data Format

Each JSON file in the `dialogues` directory contains one dialogue in the following format:

| Key                        | Value                                                                             |
|----------------------------|-----------------------------------------------------------------------------------|
| "AnonymizedUserWorkerID"   | String that is unique for each worker but unrelated to the worker's AMT Worker ID |
| "AnonymizedWizardWorkerID" | String that is unique for each worker but unrelated to the worker's AMT Worker ID |
| "BatchID"                  | We collected dialogues in batches, identified by this ID                          |
| "CompletionLevel"          | Can be "Complete", "EarlyDisconnectDuringDialogue", or "DisconnectDuringDialogue" |
| "DialogueID"               | Unique ID of this dialogue                                                        |
| "Events"                   | List of events representing the dialogue                                          |
| "FORMAT-VERSION"           |                                                                                   |
| "Scenario"                 | Dictionary containing information about the scenario of this dialogue             |
| "UserQuestionnaire"        | List of question/answer pairs for questions given to the user                     |
| "WizardQuestionnaire"      | List of question/answer pairs for questions given to the wizard                   |
