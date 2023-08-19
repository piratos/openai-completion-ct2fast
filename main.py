from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any, Union
from hf_hub_ctranslate2 import GeneratorCT2fromHfHub
import time
import shortuuid
import os


app = FastAPI()

# Load pre-trained model
if os.environ.get("MODEL_PATH"):
    MODEL_NAME = os.environ.get("MODEL_PATH")
else:
    raise Exception("MODEL_PATH env variable not defined")

model = GeneratorCT2fromHfHub(model_name_or_path=MODEL_NAME)

# Models
class ErrorResponse(BaseModel):
    object: str = "error"
    message: str
    code: int

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0

class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[Any]]
    suffix: Optional[str] = None
    temperature: Optional[float] = 0.7
    n: Optional[int] = 1
    max_tokens: Optional[int] = 50
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    logprobs: Optional[int] = None
    echo: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class CompletionResponseChoice(BaseModel):
    index: int
    text: str
    logprobs: Optional[int] = None
    finish_reason: Optional[Literal["stop", "length"]] = None


class CompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{shortuuid.random()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionResponseChoice]
    usage: UsageInfo


class CompletionResponseStreamChoice(BaseModel):
    index: int
    text: str
    logprobs: Optional[float] = None
    finish_reason: Optional[Literal["stop", "length"]] = None


class CompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"cmpl-{shortuuid.random()}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    choices: List[CompletionResponseStreamChoice]

@app.post("/completions", response_model=CompletionResponse)
async def completion(completion_request: CompletionRequest):
    try:
        print(f"[+] Request data: {completion_request}")
        # Generate response from the model
        output = model.generate(
            text=completion_request.prompt,
            max_length=completion_request.max_tokens,
            include_prompt_in_result=False
        )

        print(f"[+] LLM output: {output}")
        choices = []
        # langchain/Docsgpt expect 3 choices so we repeat the same
        for i in range(3):
            choices.append(CompletionResponseChoice(index=i, text=output[0]))
        usage_info = UsageInfo()
        response = CompletionResponse(
            model=completion_request.model,
            choices=choices,
            usage=usage_info
        )
        print(f"[+] Response {response}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

