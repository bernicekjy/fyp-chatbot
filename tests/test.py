from kb.AN_RL_KnowledgeBase import RLKnowledgeBaseManager

kb = RLKnowledgeBaseManager()

kb.add_unanswered_question(new_question="Question2")

print("Result of adding answer to question: ",kb.add_answer_to_question(question="Question3", answer="Answer1"))
print("Unanswered questions: ",kb.get_unanswered_questions())

print(kb.generate_qna_str())