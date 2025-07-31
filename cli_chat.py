# cli_chat.py (Updated with Intelligent Router Logic)
import os
import sys
import logging
import rag_system

# Configure logging to show info messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    A command-line interface to test the multi-source RAG system.
    """
    # --- 1. Verify Knowledge Files Exist ---
    required_files = ['factual_kb.txt', 'conversational_rules.txt', 'commands.txt']
    for file in required_files:
        if not os.path.exists(file):
            print(f"\n❌ ERROR: Required knowledge file not found: '{file}'")
            print("   Please make sure all three .txt files are in the same directory.\n")
            return

    session_id = "cli-test-session"

    # --- 2. Initialize RAG System ---
    print("\n--- Initializing System & Loading Knowledge Files... ---")
    rag_system.initialize_rag_system()
    rag_instance = rag_system.RAGSystem()
    openai_client = rag_system.openai_client 

    # --- 3. Process the Factual Knowledge Base ---
    print("\n--- Processing factual_kb.txt for RAG... ---")
    success = rag_instance.add_factual_kb(session_id, 'factual_kb.txt')
    if not success:
        print("❌ Failed to process the factual knowledge base. Exiting.")
        return
    print("✅ System is ready. You can now chat.")

    # --- 4. Start the Interactive Chat Loop ---
    print("\n--- Starting Chat Session ---")
    print("🤖 Ask me anything about The Fitness Doctor!")
    print("   Type 'quit' or press Ctrl+C to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue

            print("Bot: Thinking...")

            # ### REFACTOR: The Intelligent Router Logic ###
            
            # Tier 1: Check for a direct command (fastest)
            command_response = rag_instance.check_for_command(user_input)
            if command_response:
                print(f"Bot: {command_response}\n")
                continue

            # Tier 2: Check for a conversational rule (fast)
            rule_response = rag_instance.check_for_conversational_rule(user_input)
            if rule_response:
                print(f"Bot: {rule_response}\n")
                continue

            # Tier 3: If no command or rule, use RAG for a factual question (most powerful)
            context = rag_instance.get_context_for_question(session_id, user_input)
            if not context:
                # This can now be one of the conversational rules, e.g., for fallback.
                fallback_response = rag_instance.check_for_conversational_rule("fallback_unsure")
                reply_text = fallback_response if fallback_response else "I'm sorry, I don't have information on that topic. Can I help with anything else?"
                print(f"Bot: {reply_text}\n")
            else:
                # Ask the LLM to generate a response based on the retrieved context
                final_generation_prompt = f"""
                You are Alex, a friendly and helpful assistant for The Fitness Doctor. 
                Your personality is positive, supportive, and you use emojis where appropriate. 😊
                
                Based ONLY on the following context, please answer the user's question.
                Do not make up any information.
                
                CONTEXT:
                ---
                {context}
                ---
                
                QUESTION: {user_input}
                
                Answer:
                """
                try:
                    final_response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": final_generation_prompt}],
                        temperature=0.1
                    )
                    answer = final_response.choices[0].message.content.strip()
                    print(f"Bot: {answer}\n")
                except Exception as e:
                    logging.error(f"Error during final answer generation: {e}", exc_info=True)
                    print("Bot: ❌ I encountered an error while formulating my response.\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logging.error(f"A critical error occurred in the chat loop: {e}", exc_info=True)
            break

if __name__ == "__main__":
    main()