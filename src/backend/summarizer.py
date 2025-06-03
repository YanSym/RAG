from helper_methods import (
    get_llm_response,
    extract_text_from_file,
)
from prompts.prompts import PROMPT_SUMMARIZER


class Summarizer:
    def __init__(self, parameters):
        self.parameters = parameters

    def summarize_text(self, text, word_limit, additional_info):
        if additional_info:
            additional_info = f"Informações adicionais: {additional_info}"
        prompt = PROMPT_SUMMARIZER.format(
            text=text, word_limit=word_limit, additional_info=additional_info
        )
        return get_llm_response(prompt, self.parameters, 0)

    def process_documents(self, file_paths, word_limit, summarize_all, additional_info):
        summaries = {}
        if summarize_all:
            combined = ""
            for f in file_paths:
                combined += extract_text_from_file(f) + "\n\n"
            summaries["_All_Docs_"] = self.summarize_text(
                combined, word_limit, additional_info
            )
        else:
            for f in file_paths:
                try:
                    f_str = f.split("\\")[-1]
                except Exception:
                    pass
                extraction = extract_text_from_file(f)
                if extraction:
                    summaries[f_str] = self.summarize_text(
                        extraction, word_limit, additional_info
                    )
        return summaries
