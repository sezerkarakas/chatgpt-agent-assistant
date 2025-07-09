from agents import Agent, FileSearchTool, Runner, TResponseInputItem ,function_tool
from dotenv import load_dotenv
from tools import local_file_search

load_dotenv()

@function_tool        
def end_conversation():
    """
    Call this tool when the user no longer needs help, says goodbye, or expresses
    gratitude (e.g., 'thanks', 'goodbye', 'see you'). This tool ends the conversation.
    """
    print("\nAsistan: Görüşmek üzere! Monster Asistanı her zaman yanınızda.\n")
    exit()


# Sistem promptunu yükle
try:
    with open('gpt_prompt_sakali.md', 'r', encoding='utf-8') as file:
        system_instructions = file.read()
except FileNotFoundError:
    print("Hata: gpt_prompt.md dosyası bulunamadı!")
    exit()


agent = Agent(
    name="Monster Technical Assistant",
    instructions=system_instructions,
    model="gpt-4o-mini",  # Veya local LLM
    tools=[
        local_file_search,
        end_conversation
    ],
)

print(agent)

print("-----------------------------------------------------")

async def main():
    convo: list[TResponseInputItem] =[]

    opening = "Merhaba, ben Monster Teknik Asistan! Size nasıl yardımcı olabilirim?"
    print(f"Asistan: {opening}\n")
    convo.append({"content": opening, "role": "assistant"})

    while True:
        user_input = input("Siz: ")
        
        if user_input.lower() == '':
            print("\nAsistan: Görüşmek üzere! Monster Asistanı her zaman yanınızda.\n")
            break
        
        convo.append({"content": user_input, "role": "user"})
        result = await Runner.run(agent, convo)
        
        print(f"\nAsistan: {result.final_output}\n")
        convo = result.to_input_list()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())