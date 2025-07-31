#  			    Test Plan for RAG-Bot





## 

## Category 1: Factual Knowledge Retrieval (from factual\_kb.txt)





#### Goal: Test the core RAG functionality. Can the bot find and summarize information from the main knowledge base?





***Direct Question: where are you located?***

***Expected Behavior: Should respond that it's globally available online.***



***Direct Question: who is robbie stahl?***

***Expected Behavior: Should give a summary of Robbie Stahl's experience and background.***



***Slightly Rephrased Question: tell me about the fitness doctor***

***Expected Behavior: Should explain what the organization is, who it's for, and that it was founded by Robbie Stahl.***



***Deeper "Why" Question: what is so special about the fitness doctor?***

***Expected Behavior: Should mention personalized care, cutting-edge techniques, holistic approach, and virtual accessibility.***



***Target Audience Question: who should use this program?***

***Expected Behavior: Should list the types of individuals the program is for (e.g., those with chronic pain, seeking to improve mobility).***



***Specific Session Question: what is the it's all about you session?***

***Expected Behavior: Should describe the free, 90-minute semi-private discovery session.***



***Logistical Question: how long does the all about you session take?***

***Expected Behavior: Should state it's 90 minutes but might run longer.***



***Cost-Related Question: is the all about you session free?***

***Expected Behavior: Should confirm it's 100% free but that spots are limited.***



***Event Definition Question: what is the full body fix event?***

***Expected Behavior: Should describe it as a live therapeutic fitness event for people 50+.***





##  

##  

## Category 2: Conversational Rules \& Bot Persona (from conversational\_rules.txt)





#### Goal: Test the bot's ability to handle common conversational phrases and maintain its persona ("Alex"). This tests your rules-based logic or how well the RAG system handles conversational text.







***Bot Identity: who am I talking to? (or what's your name?)***

***Expected Behavior: Should respond with: "This is Alex, the Director of Client Success at The Fitness Doctor. I'm here to help!"***



***Bot Intent: why are you messaging me?***

***Expected Behavior: Should respond by offering the "All About You" bonus session.***



***Small Talk: how are you doing?***

***Expected Behavior: Should respond with: "I'm doing great, thank you for asking!"***



***Hardware Requirements: do I need a camera for the session?***

***Expected Behavior: Should confirm that camera and audio need to be on for the interactive session.***



***Spouse/Partner Query: can my wife join the call?***

***Expected Behavior: Should encourage partners to join, especially if financial decisions are made together.***



***Rescheduling Request: I need to reschedule my appointment***

***Expected Behavior: Should provide instructions to email Patricia at her email address.***



***Correction Handling: that's wrong (or you have the wrong information)***

***Expected Behavior: Should respond with a polite apology like: "I'm really sorry for the mix-up! Thank you for pointing that out..."***



***User Discomfort: it's a bad time to talk***

***Expected Behavior: Should respond with an understanding message and offer to continue via email.***





##  

## 

## Category 3: Complex Scenarios \& Multi-Turn Interactions





#### Goal: Test how the bot handles situations that might require logic or specific flows.





***Missed Session Flow: I missed the session, can I get the replay?***

***Expected Behavior: Should provide the link: https://www.thefitnessdoctor.com/fbf-event/the-full-body-fix-event and potentially upsell the "All About You" session.***



***Scheduling Conflict (Part 1): that time doesn't work for me***

***Expected Behavior: Should offer alternative time slots (even if they are placeholders like \[Insert Available Time Slot 1]).***



***Scheduling Conflict (Part 2): none of those times work for me either***

***Expected Behavior: Should understand the previous context and offer the paid Private Consultation with the link.***



***Event Schedule Request: what are the dates for the next full body fix?***

***Expected Behavior: Should first ask for the user's timezone before providing the schedule. (This is an advanced test of its logic).***



***User Hesitation: I want to wait until after the fbf to decide***

***Expected Behavior: Should acknowledge the user's focus but create urgency by highlighting the limited spots for the "All About You" session.***



***Already Booked Scenario: I already scheduled a consultation***

***Expected Behavior: Should give a positive and concluding response like: "That's fantastic! It's great to hear..."***





##  

## Category 4: Edge Cases \& Fallbacks





#### Goal: Test what the bot does when it doesn't know the answer or receives an unexpected input.





***Command Handling: stop***

***Expected Behavior: Should respond with the unsubscribe message: "You have been successfully unsubscribed..."***



***Nonsense Question: what is the color of the sky on mars?***

***Expected Behavior: Should trigger the fallback response: "I'm sorry, I didn't quite catch that. Could you rephrase your question?" (or similar).***



***Very Short Input: ok***

***Expected Behavior: Should be ignored by the is\_a\_question filter and not produce a response.***



***Gibberish: asdfghjkl***

***Expected Behavior: Should also trigger the fallback response.***

