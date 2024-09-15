import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random as rnd
import re
import ast
import io
import contextlib
from funcs_file import get_tools
from funcs_file import get_globals


# TO FIX: code-interpreter needs to import and use libraries
# does it need to execute anything other than python?
# fix to be able to access databases and return useful info


class chat:
    def __init__(self, model="NousResearch/Hermes-2-Pro-Llama-3-8B", tools=None):
        self.device = "cuda"
        self.tokenizer = AutoTokenizer.from_pretrained(model, device_map="auto")
        self.model = AutoModelForCausalLM.from_pretrained(model, device_map="auto")
        self.DEF_PRMPT = """\
        Your name is MaqsamBot, you have been created and developed by Maqsam.
        You are a helpful, respectful and honest assistant with a deep knowledge of code and software design. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
        For code generation: in case of generating python code, only use legal and executable python statements and syntax. DO NOT use syntax that will not run with a python interpreter
        **IMPRTANT**: assume all necessary packages and libraries called by the generated code are installed and ready to use
        **AVAILABLE DATA**: these are data files you can access, they are stored locally and can be accessed directly
        AVAILABLE DATA:
        calls_history.csv: a csv containing 8 columns described as follows:
        operator: name of telecom company making the call
        Indoor_Outdoor_Travelling: whether call was taken indoor, outdoor, or travelling
        Network Type; type of network 2G, 3G, 4G
        Rating: call rating for call
        Call Drop Category: reason why call was ended
        Latitude: latitude of person making the call
        Longituage: longitude of person making the call
        State Name: name of state where call was made
        """
        self.chat = [
            {"role": "system", "content": self.DEF_PRMPT},
        ]
        self.template = ""
        self.code = ""
        self.response_text = []
        self.only_text = ""
        self.pattern = r"```(?:python)?(.*?)```"
        self.tools = tools
        self.globals = get_globals()

    def __get_call(self, func):
        reg = r"<tool_call>(.*?)</tool_call>"
        matches = re.findall(reg, func, re.DOTALL)
        if matches:
            call = ast.literal_eval(matches[0].strip())
            if self.globals.get(call["name"]) == None:
                return None
            return call
        return None

    def __execute_function(self, func_dict):
        func_name = func_dict.get("name")
        func_args = func_dict.get("arguments", [])
        func = self.globals.get(func_name)

        return func(*func_args)

        # generate a random ID for the function call

    def __gen_id(self):
        # ids should be unique within a chat
        # might store in a set
        chrs = [chr(rnd.randint(ord("A"), ord("Z"))) for i in range(3)]
        nums = [(str(rnd.randint(0, 9))) for i in range(3)]
        id = "".join(chrs + nums)

        return id

    def __extract_text(self, text):
        # Different re depending on LLM model used
        # reg=r'(<\|CHATBOT_TOKEN\|>)(.*?)(?:<\|END_OF_TURN_TOKEN\|>)'
        # reg=r'(<\|im_end\|>assistant)(.*?)(?=\s*<\|im_end\|>)'
        reg = r"(<\|im_start\|>assistant)(.*?)(?:<\|im_end\|>)"

        matches = re.findall(reg, text, re.DOTALL)
        return matches[-1][1]

    def gen(self):

        self.template = self.tokenizer.apply_chat_template(
            self.chat, tokenize=False, add_generation_prompt=True, content=""
        )

        input_tokens = self.tokenizer(self.template, return_tensors="pt")

        for i in input_tokens:
            input_tokens[i] = input_tokens[i].to(self.device)

        output = self.model.generate(**input_tokens, max_new_tokens=900)

        output = self.tokenizer.batch_decode(output, clean_up_tokenization_spaces=True)

        self.response_text.append(output[0])

        display = self.__extract_text(output[0])
        return display

    def function_call(self, tools):
        # tokenize user prompt and define tools to user
        func_inputs = self.tokenizer.apply_chat_template(
            self.chat,
            chat_template="tool_use",
            tools=tools,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        func_inputs = {k: v.to(self.model.device) for k, v in func_inputs.items()}
        # .generate returns documentation of the tools used + instructions to the LLM on how to use
        #  funcitons and extract arguments from prompt
        func_out = self.model.generate(**func_inputs, max_new_tokens=900)
        # func_call stores the arguments and name of the function that will be used in dict format
        func_call = self.tokenizer.decode(
            func_out[0][len(func_inputs["input_ids"][0]) :]
        )
        return func_call

    def run_function(self, call_dict):
        tool_call_id = self.__gen_id()
        tool_call = {"name": call_dict["name"], "arguments": call_dict["arguments"]}
        self.chat.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {"id": tool_call_id, "type": "function", "function": tool_call}
                ],
                "content": "",
            }
        )
        # takes dict with function name and args and returns result of function execution
        self.chat.append(
            {
                "role": "tool",
                "tool_call_id": id,
                "name": call_dict["name"],
                "content": str(self.__execute_function(call_dict)),
            }
        )
        # generates final query for user. Contains message form LLM and results returned from funciton call
        inputs = self.tokenizer.apply_chat_template(
            self.chat,
            chat_template="tool_use",
            tools=self.tools,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        out = self.model.generate(**inputs, max_new_tokens=128)
        answer = self.tokenizer.decode(out[0][len(inputs["input_ids"][0]) :])
        reg = r"(.*?)(?=\s*<\|im_end\|>)"
        matches = re.findall(reg, answer, re.DOTALL)
        answer = matches[0]
        return answer

    def extract_python_code(self, response_text):
        matches = re.findall(self.pattern, response_text, re.DOTALL)
        if matches:
            print("RUN 2----------")
            self.code = matches[0]
            return matches[0]
        else:
            return "NAN"

    def run_code(self, response):
        response = self.extract_python_code(response)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(response)
        return output.getvalue()

    def __append_chat(self, role, content):
        self.chat.append({"role": role, "content": content})

    def run_n_branch(self, messages):
        self.chat = messages
        response = self.gen()
        code_result = ""

        print("RESULT:::")
        print(response)
        print("------------")

        if self.tools:
            call = self.function_call(self.tools)
            if self.__get_call(call):
                call = self.__get_call(call)
                response = self.run_function(call)
                return response, code_result

        if self.extract_python_code(response) != "NAN":
            print("RUN 1-----------")
            code_result = self.run_code(response)

        return response, code_result

    def get_chat(self):
        return self.chat