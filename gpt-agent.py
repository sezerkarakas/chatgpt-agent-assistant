from agents import Agent, FileSearchTool, Runner, TResponseInputItem
from dotenv import load_dotenv

load_dotenv()

# Sistem promptunu yükle
try:
    with open('gpt_prompt_v4.md', 'r', encoding='utf-8') as file:
        system_instructions = file.read()
except FileNotFoundError:
    print("Hata: gpt_prompt.md dosyası bulunamadı!")
    exit()
agent = Agent(
    name="Monster Technical Assistant",
    instructions=system_instructions,
    model="gpt-4o-mini",
    tools=[
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_680f2bfd7e808191ba899667c4fabf14"],
        ),
    ],
)
print(agent)

print("-----------------------------------------------------")

async def main():
    convo: list[TResponseInputItem] =[]
    while True:
        user_input = input("Siz: ")
        
        if user_input.lower() == 'exit':
            print("\nAsistan: Görüşmek üzere! Monster Asistanı her zaman yanınızda.\n")
            break
        
        convo.append({"content": user_input, "role": "user"})
        result = await Runner.run(agent, convo)
        
        print(f"\nAsistan: {result.final_output}\n")
        
        convo = result.to_input_list()
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())