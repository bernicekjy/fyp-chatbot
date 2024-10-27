from Narelle import Narelle

sample_conversation = {
    "_id": {"$oid": "65f172e8192f78bab2a94539"},
    "stime": {"text": "2024-03-13 17:33:28", "timestamp": 1710322408.501202},
    "messages": [
        {
            "role": "user",
            "content": "is there lab next week?",
            "recorded_on": {
                "text": "2024-03-13 17:33:56",
                "timestamp": 1710322436.547978,
            },
        },
        {
            "role": "ai",
            "content": "There will be no lab session next week as it is Recess Week. \n\n\n **Sources:** *['FAQs about the Course', 'Course Calendar', 'NTU Learn - Announcements Page']*",
            "recorded_on": {
                "text": "2024-03-13 17:34:03",
                "timestamp": 1710322443.800639,
            },
            "token_cost": {"cost": "0.00392550", "tokens": 2612},
        },
        {
            "role": "user",
            "content": "what week is it now",
            "recorded_on": {
                "text": "2024-03-13 17:34:21",
                "timestamp": 1710322461.171272,
            },
        },
        {
            "role": "ai",
            "content": "I'm sorry, I don't have access to real-time information. Could you please check the course calendar or NTULearn to confirm which week it is currently? ",
            "recorded_on": {
                "text": "2024-03-13 17:34:25",
                "timestamp": 1710322465.632266,
            },
            "token_cost": {"cost": "0.00417000", "tokens": 2769},
        },
        {
            "role": "user",
            "content": "what is the deadline for my assignment",
            "recorded_on": {
                "text": "2024-03-13 17:34:54",
                "timestamp": 1710322494.562975,
            },
        },
        {
            "role": "ai",
            "content": "I'm sorry, I don't have access to real-time information about your specific assignment deadline. Please check the assignment details and instructions provided by your instructor on NTULearn or in class to confirm the deadline. If you are unable to find the deadline, you can email your instructor for clarification. ",
            "recorded_on": {
                "text": "2024-03-13 17:35:05",
                "timestamp": 1710322505.071112,
            },
            "token_cost": {"cost": "0.00403300", "tokens": 2669},
        },
        {
            "role": "user",
            "content": "what is the deadline for my assignment",
            "recorded_on": {
                "text": "2024-03-13 17:35:12",
                "timestamp": 1710322512.711009,
            },
        },
        {
            "role": "ai",
            "content": "I'm sorry, I don't have access to real-time information about your specific assignment deadline. Please check the assignment details and instructions provided by your instructor on NTULearn or in class to confirm the deadline. If you are unable to find the deadline, you can email your instructor for clarification. ",
            "recorded_on": {
                "text": "2024-03-13 17:35:18",
                "timestamp": 1710322518.225166,
            },
            "token_cost": {"cost": "0.00414700", "tokens": 2745},
        },
    ],
    "last_interact": {"text": "2024-03-13 17:35:18", "timestamp": 1710322518.225371},
    "llm_deployment_name": "asknarelle-experimental-gpt-35-turbo",
    "llm_model_name": "gpt-3.5-turbo-instruct",
    "vectorstore_index": "vector-sc1015-ay23t2-b",
    "overall_cost": {"overall_cost": 0.0162755, "overall_tokens": 10795},
    "Person": "44793f1faad064b52f6716c2c4b0633e",
}

if __name__ == "__main__":
    bot = Narelle()

    while True:
        query = input("Enter your query: ")
        bot.answer_this(query)
        print("-------")
