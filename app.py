import asyncio
import uuid
import gradio as gr
import edge_tts
from deep_translator import GoogleTranslator
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch

# ===== Voice setup =====

voice_characters = {
    "English - US": {
        "Aria": "en-US-AriaNeural",
        "Jenny": "en-US-JennyNeural",
        "Guy": "en-US-GuyNeural",
    },
    "English - India": {
        "Neerja": "en-IN-NeerjaNeural",
        "Prabhat": "en-IN-PrabhatNeural"
    },
    "Hindi": {
        "Swara": "hi-IN-SwaraNeural",
        "Madhur": "hi-IN-MadhurNeural",
        "Neerja (Hindi Style)": "hi-IN-NeerjaNeural",  # More natural Hindi TTS
    },
    "Tamil": {
        "Pallavi": "ta-IN-PallaviNeural"
    },
    "Telugu": {
        "Shruti": "te-IN-ShrutiNeural"
    },
    "Kannada": {
        "Sapna": "kn-IN-SapnaNeural"
    },
    "Malayalam": {
        "Midhun": "ml-IN-MidhunNeural"
    },
    "Gujarati": {
        "Dhwani": "gu-IN-DhwaniNeural"
    },
    "Punjabi": {
        "Harpreet": "pa-IN-HarpreetNeural"
    },
    "Marathi": {
        "Aarohi": "mr-IN-AarohiNeural"
    },
}


async def generate_tts(text, voice):
    if not text.strip():
        raise ValueError("Input text is empty")
    filename = f"output_{uuid.uuid4()}.mp3"
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(filename)
    return filename

def tts_wrapper(text, language, character, translation_direction):
    try:
        original_text = text.strip()
        if not original_text:
            return "⚠️ Please enter some text.", None

        if translation_direction == "English to Hindi":
            text = GoogleTranslator(source='en', target='hi').translate(original_text)
        elif translation_direction == "Hindi to English":
            text = GoogleTranslator(source='hi', target='en').translate(original_text)

        voice = voice_characters.get(language, {}).get(character)
        if not voice:
            return f"⚠️ Voice '{character}' not available for '{language}'.", None

        filename = asyncio.run(generate_tts(text, voice))
        return text, filename

    except Exception as e:
        return f"❌ Error: {str(e)}", None

def get_characters(language):
    chars = list(voice_characters.get(language, {}).keys())
    default_char = chars[0] if chars else None
    return gr.update(choices=chars, value=default_char)

# ===== Chatbot setup =====

model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
device = torch.device("cpu")
model.to(device)

async def generate_bot_tts(text):
    voice = voice_characters["English - US"]["Aria"]
    filename = await generate_tts(text, voice)
    return filename

def chatbot_response(history, user_message):
    if history is None:
        history = []

    history.append(("You", user_message))
    conversation_text = " ".join([msg for _, msg in history])
    inputs = tokenizer([conversation_text], return_tensors="pt").to(device)

    reply_ids = model.generate(**inputs, max_length=200)
    response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    history.append(("Bot", response))

    chat_str = "\n".join([f"{speaker}: {msg}" for speaker, msg in history])

    try:
        audio_path = asyncio.run(generate_bot_tts(response))
    except Exception as e:
        audio_path = None
        print(f"TTS failed: {e}")

    return history, chat_str, audio_path

# ===== CSS with animations and glitch =====

custom_css = """
body {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #000000);
    background-size: 600% 600%;
    animation: gradientBG 15s ease infinite;
    font-family: 'Courier New', monospace;
    color: #00FF00;
}

.gradio-container {
    border: 2px solid #00FF00;
    padding: 20px;
    box-shadow: 0 0 10px #00FF00;
    border-radius: 10px;
}

h1 {
    position: relative;
    font-family: 'Courier New', monospace;
    color: #00FF00;
    border-right: 2px solid #00FF00;
    white-space: nowrap;
    overflow: hidden;
    width: fit-content;
    animation: typewriter 3s steps(40, end), blinkCaret 0.8s step-end infinite;
}

h1::after {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    color: #ff00c8;
    clip: rect(0, 900px, 0, 0);
    animation: glitch 2s infinite linear alternate-reverse;
}

@keyframes glitch {
    0% { clip: rect(42px, 9999px, 44px, 0); transform: skew(0.5deg); }
    5% { clip: rect(12px, 9999px, 15px, 0); transform: skew(0.3deg); }
    10% { clip: rect(85px, 9999px, 88px, 0); transform: skew(0.2deg); }
    15% { clip: rect(24px, 9999px, 27px, 0); transform: skew(0.4deg); }
    20% { clip: rect(61px, 9999px, 65px, 0); transform: skew(0.2deg); }
    25% { clip: rect(10px, 9999px, 14px, 0); transform: skew(0.3deg); }
    30% { clip: rect(50px, 9999px, 53px, 0); transform: skew(0.1deg); }
    35% { clip: rect(20px, 9999px, 24px, 0); transform: skew(0.5deg); }
    40% { clip: rect(65px, 9999px, 69px, 0); transform: skew(0.3deg); }
    100% { clip: rect(0, 9999px, 0, 0); transform: skew(0deg); }
}

.gr-button {
    background: black;
    color: #00FF00 !important;
    font-weight: bold;
    border: 1px solid #00FF00;
    box-shadow: 0 0 5px #00FF00;
    animation: bounce 2s infinite;
}

.gr-textbox, .gr-dropdown {
    background: black;
    color: #00FF00;
    border: 1px solid #00FF00;
    box-shadow: inset 0 0 5px #00FF00;
}

.gr-audio {
    box-shadow: 0 0 10px #00FF00;
    border-radius: 10px;
}

#chat_display {
    background: black;
    color: #00FF00;
    padding: 10px;
    border: 1px solid #00FF00;
    box-shadow: inset 0 0 10px #00FF00;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    animation: typewriter 3s steps(100, end);
}

@keyframes typewriter {
    from { width: 0 }
    to { width: 100% }
}

@keyframes blinkCaret {
    0%, 100% { border-color: transparent }
    50% { border-color: #00FF00; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
"""

# ===== UI =====

def create_app():
    with gr.Blocks(css=custom_css) as app:

        gr.HTML("<h1 data-text='🗣️ SpeakEasy AI'>🗣️ SpeakEasy AI</h1>")

        with gr.Tab("🎧 Text to Speech + Translator"):
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(label="💬 Your Text", placeholder="Enter text here...", lines=4)
                    language_dropdown = gr.Dropdown(choices=list(voice_characters.keys()), value="English - US", label="🌐 Language")
                    character_dropdown = gr.Dropdown(choices=list(voice_characters["English - US"].keys()), value="Aria", label="🧑‍🎤 Voice Character")
                    with gr.Accordion("🔁 Translation Options", open=False):
                        translation_dropdown = gr.Dropdown(choices=["None", "English to Hindi", "Hindi to English"],
                                                           value="None", label="🔄 Translate Text")

                    tts_button = gr.Button("🎙️ Generate Voice")
                    output_text = gr.Textbox(label="📝 Final Output / Translation")
                with gr.Column(scale=1):
                    output_audio = gr.Audio(label="🔊 Listen Here", autoplay=True)

            language_dropdown.change(fn=get_characters, inputs=language_dropdown, outputs=character_dropdown)

            def tts_with_loading(*args):
                yield "Processing...", None
                yield tts_wrapper(*args)

            tts_button.click(
                fn=tts_with_loading,
                inputs=[text_input, language_dropdown, character_dropdown, translation_dropdown],
                outputs=[output_text, output_audio]
            )

        with gr.Tab("🤖 Chatbot"):
            with gr.Row():
                with gr.Column(scale=2):
                    user_input = gr.Textbox(label="💬 Ask Anything", lines=2, placeholder="Try: What's your name?")
                    chat_display = gr.Textbox(label="📜 Conversation", interactive=False, lines=15, elem_id="chat_display")
                    send_button = gr.Button("📩 Send")
                with gr.Column(scale=1):
                    audio_output = gr.Audio(label="🔊 Bot's Voice Reply", autoplay=True)

            chat_history = gr.State([])

            def chatbot_with_typing(history, user_message):
                yield history, "Bot is typing...", None
                yield chatbot_response(history, user_message)

            send_button.click(
                fn=chatbot_with_typing,
                inputs=[chat_history, user_input],
                outputs=[chat_history, chat_display, audio_output]
            )

            user_input.submit(
                fn=chatbot_with_typing,
                inputs=[chat_history, user_input],
                outputs=[chat_history, chat_display, audio_output]
            )

        gr.HTML("<footer style='text-align:center;padding:10px;color:#00FF00;'>🔧 Made by using Gradio, Edge TTS, and Hugging Face 🤗</footer>")

    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(share=True)
