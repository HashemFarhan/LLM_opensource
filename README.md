# **Chat With Your Data (CWYD)**

## **_Overview_**

#### This project aims to allow Maqsam's clients to explore and understand their data and harness the power of analytics through powerful LLM engines.

#### The complexities of the underlying LLM processes is masked by a simple and user-friendly interface with unique sessions for each user.

#### The current pipeline is built using the [`Hermes-2-Pro`](https://huggingface.co/NousResearch/Hermes-2-Pro-Llama-3-8B) LLM, which is a version of `Llama-3-8B` and is finetuned for function calling

#### This new version of Hermes maintains its excellent general task and conversation capabilities - but also performs well on function calling, JSON Structured Outputs, and has improved on several other metrics as well.

## **_Features_**

- #### Code-interpreter
- #### Function calling
- #### Database access
- #### RAG

## **_Installation_**

### To setup:

1. Clone the repository using the following command: <br />

```bash
git clone ssh://git@phabricator.corp.maqsam.com/source/hatchery.git
```

2. Navigate to the required directory:

```bash
cd /workspace/hatchery/opensource_cwyd/latest_code
```

3. Install required files:

```bash
pip install -r requirements.txt
```

## **_Usage_**

The `interface.py` file is connected to all the necessary files.
<br />
To execute: <br />

```bash
streamlit run interface.py
```

> NOTE <br />
> A HuggingFace token may be required to use the LLM model

#### **_HuggingFace Login_**

1. Install HuggingFace CLI

```bash
 pip install -U "huggingface_hub[cli]"
```

2. Run the following command to login and paste your HF token:

```bash
huggingface-cli login
```
