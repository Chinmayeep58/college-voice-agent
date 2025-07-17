# from dotenv import load_dotenv
# from livekit import agents
# from livekit.agents import AgentSession, Agent, RoomInputOptions
# from livekit.plugins import (
#     openai,
#     cartesia,
#     assemblyai,
#     noise_cancellation,
#     silero,
# )

# load_dotenv()


# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(instructions="You are a helpful AI assistant. Keep your responses concise and conversational. You're having a real-time voice conversation, so avoid long explanations unless asked.")


# async def entrypoint(ctx: agents.JobContext):
#     await ctx.connect()

#     # Create agent session with AssemblyAI's advanced turn detection
#     session = AgentSession(
#         stt=assemblyai.STT(
#             end_of_turn_confidence_threshold=0.7,
#             min_end_of_turn_silence_when_confident=160,
#             max_turn_silence=2400,
#         ),
#         llm=openai.LLM(
#             model="gpt-4o-mini",
#             temperature=0.7,
#         ),
#         tts=cartesia.TTS(),
#         vad=silero.VAD.load(),  # Voice Activity Detection for interruptions
#         turn_detection="stt",  # Use AssemblyAI's STT-based turn detection
#     )

#     await session.start(
#         room=ctx.room,
#         agent=Assistant(),
#         room_input_options=RoomInputOptions(
#             noise_cancellation=noise_cancellation.BVC(),
#         ),
#     )

#     # Greet the user when they join
#     await session.generate_reply(
#         instructions="Greet the user and offer your assistance."
#     )


# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))





from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    assemblyai,
    noise_cancellation,
    silero,
)

load_dotenv()

# 🗓️ Static schedule to inject into prompt
college_schedule = {
    "monday": [
        {"time": "9:00 AM", "subject": "Mathematics", "location": "Room 101"},
        {"time": "11:00 AM", "subject": "Physics", "location": "Room 105"},
    ],
    "tuesday": [
        {"time": "10:00 AM", "subject": "Computer Science", "location": "Room 202"},
    ],
    "wednesday": [],
    "thursday": [
        {"time": "1:00 PM", "subject": "Chemistry Lab", "location": "Lab 1"},
    ],
    "friday": [
        {"time": "9:00 AM", "subject": "English", "location": "Room 103"},
        {"time": "11:00 AM", "subject": "Biology", "location": "Room 107"},
    ],
    "saturday": [],
    "sunday": [],
}


def schedule_to_text(schedule: dict) -> str:
    result = []
    for day, entries in schedule.items():
        if entries:
            result.append(f"\n{day.capitalize()}:")
            for item in entries:
                result.append(f"- {item['time']}: {item['subject']} in {item['location']}")
        else:
            result.append(f"\n{day.capitalize()}: No classes.")
    return "\n".join(result)


# 🧠 Agent with schedule embedded in instructions
class Assistant(Agent):
    def __init__(self) -> None:
        full_schedule_text = schedule_to_text(college_schedule)
        super().__init__(
            instructions=(
                "You are a helpful AI assistant. You are aware of the user's weekly college schedule:\n"
                f"{full_schedule_text}\n\n"
                "Answer any questions about the schedule. Keep your responses short and conversational."
            )
        )


# 🚀 Entrypoint
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=assemblyai.STT(
            end_of_turn_confidence_threshold=0.7,
            min_end_of_turn_silence_when_confident=160,
            max_turn_silence=2400,
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection="stt",
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and tell them you can help with their class schedule."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
