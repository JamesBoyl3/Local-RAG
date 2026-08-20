from localrag import RAGModel, DocumentChunk

from unittest.mock import Mock, MagicMock

def test_prompt_building() -> None:
	model = RAGModel.__new__(RAGModel)
	doc = DocumentChunk(src="paper1.pdf", content="abc", page_no=3)
	
	result = model._build_prompt("xyz", [doc])
	
	assert result["role"] == "user"
	assert "abc" in result["content"]
	assert "xyz" in result["content"]

#def test_ingestion() -> None: 
#	sql_manager = SQLManager("test.db")
#	vector_db = FAISSManager(384, "test.faiss")

def test_response_generation() -> None: 
	mock_llm = Mock()
	mock_llm.get_answer.return_value = "xyz"
	model = RAGModel(llm=mock_llm, doc_db=MagicMock(), vector_db=Mock(), ingestion_pipeline=Mock())
	
	answer = model.generate_response("abc")

	assert answer == "xyz"
	assert model._conversation.messages == [
        {
		"role": "system",
		"content": "You are an assistant for the International Energy Agency for District Heating and Cooling (IEA DHC).\n\n"
		"Your purpose is to help users understand district heating and cooling technologies, "
		"research papers, and publications from the IEA DHC.\n\n"
		"You must use the provided context as your primary source of information. "
		"If the provided context does not contain enough information to answer the question, state that the information is not available in the provided documents. Do not fill gaps using"
		"information not provided\n\n"
		"When answering, provide a concise and accurate summary of the relevant information. "
		"Avoid unnecessary technical detail unless requested by the user.\n\n"
		"Citations:\n"
		"When using information from the provided context, cite the source using the document title. "
		"Use the format: [Document Title, p. X].\n"
		"If multiple documents are used, cite each relevant document.\n\n"
		"Do not invent document titles, URLs, or citations. Only cite sources that are explicitly provided in the context.",
        }, 
	{
		"role": "user",
		"content": "abc"
	},
	{
		"role": "assistant", 
		"content": "xyz"
	}
	]

