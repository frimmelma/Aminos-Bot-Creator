import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import time
import base64

# Configurazione della sessione Streamlit
st.set_page_config(page_title="Chatbot Personality Creator", page_icon="🤖")

# Dizionario per il supporto multilingua (aggiornato con nuove traduzioni)
translations = {
    "en": {
        "login_title": "Login",
        "username": "Username",
        "openai_key": "OpenAI API Key",
        "login_button": "Login",
        "login_success": "Login successful!",
        "welcome": "Welcome, {}!",
        "assistant_name": "Assistant Name",
        "company_name": "Company Name",
        "assistant_purpose": "Assistant Purpose",
        "objective": "Objective",
        "personality": "Personality",
        "main_url": "Main Website URL",
        "contact_url": "Contact Page URL",
        "other_urls": "Other URLs to scrape (one per line)",
        "generate_button": "Generate Prompt",
        "custom_prompt": "Custom Prompt",
        "standard_prompt": "Standard Prompt",
        "generated_faqs": "Generated FAQs",
        "processing": "Processing...",
        "scraping_error": "Error scraping {}: {}",
        "step_scraping": "Scraping URLs...",
        "step_custom_prompt": "Generating custom prompt...",
        "step_standard_prompt": "Generating standard prompt...",
        "step_faqs": "Generating FAQs...",
        "process_complete": "Process complete!",
        "booking_url": "Booking URL",
        "purposes": ["Question Answering", "Sales", "Appointment Booking", "Consulting"],
        "personalities": ["Serious and Professional", "Friendly and Cordial", "Informal and Friendly", "Empathetic and Understanding", "Enthusiastic and Motivating"],
    },
    "it": {
        "login_title": "Accesso",
        "username": "Nome utente",
        "openai_key": "Chiave API OpenAI",
        "login_button": "Accedi",
        "login_success": "Accesso effettuato con successo!",
        "welcome": "Benvenuto, {}!",
        "assistant_name": "Nome assistente",
        "company_name": "Nome azienda",
        "assistant_purpose": "Scopo dell'assistente",
        "objective": "Obiettivo",
        "personality": "Personalità",
        "main_url": "URL principale del sito web",
        "contact_url": "URL della pagina contatti",
        "other_urls": "Altri URL da cui prendere informazioni (uno per riga)",
        "generate_button": "Genera Prompt",
        "custom_prompt": "Prompt Personalizzato",
        "standard_prompt": "Prompt Standard",
        "generated_faqs": "FAQ Generate",
        "processing": "Elaborazione in corso...",
        "scraping_error": "Errore durante lo scraping di {}: {}",
        "step_scraping": "Scraping degli URL in corso...",
        "step_custom_prompt": "Generazione del prompt personalizzato...",
        "step_standard_prompt": "Generazione del prompt standard...",
        "step_faqs": "Generazione delle FAQ...",
        "process_complete": "Processo completato!",
        "booking_url": "URL di prenotazione",
        "purposes": ["Risposta alle domande", "Vendite", "Prenotazione appuntamenti", "Consulenza"],
        "personalities": ["Serio e professionale", "Simpatico e cordiale", "Informale e amichevole", "Empatico e comprensivo", "Entusiasta e motivante"],
    }
}

def get_text(key):
    return translations[st.session_state.get('language', 'en')][key]

def login():
    language = st.selectbox("Language / Lingua", ["en", "it"])
    st.session_state['language'] = language
    st.title(get_text("login_title"))
    with st.form("login_form"):
        username = st.text_input(get_text("username"))
        login_option = st.radio("Do you have a password or an API key?", ["Password", "API Key"])
        if login_option == "Password":
            password = st.text_input("Password", type="password")
            if password == "AminosAiBOT-Creator2024!":  # Replace "your_password" with the actual password
                openai_key = "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"  # Replace "XXXXXXX" with the actual OpenAI key
        else:
            openai_key = st.text_input(get_text("openai_key"), type="password")
        submitted = st.form_submit_button(get_text("login_button"))
        if submitted:
            if username and openai_key:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['openai_key'] = openai_key
                return True
    return False

def scrape_urls(urls, status):
    content_dict = {}
    for url in urls:
        try:
            status.write(f"{get_text('step_scraping')} {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else url
            text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
            content_dict[title] = text_content
            time.sleep(1)  # Simulazione di un processo più lungo
        except Exception as e:
            st.error(get_text("scraping_error").format(url, str(e)))
    return content_dict

def generate_custom_prompt(info):
    openai.api_key = st.session_state['openai_key']
    system_prompt = f"""You are an expert in creating custom prompts for chatbots. 
    Your task is to create a highly personalized prompt based on the given information.
    The output should strictly follow this structure:
    
    CHI SEI: [brief description]
    RUOLO: [detailed role description]
    OBIETTIVO: [clear objective]
    TONO: [tone description]

    ---

    Example : 
    CHI SEI: Sei NAME, l'esperta di vendite e consulenza di HOLDING, specializzata nell'arredamento completo per uffici executive, dedicato esclusivamente agli amanti del design Made in Italy. La tua missione è invogliare e convincere i clienti a interessarsi ai prodotti e servizi di HOLDING.
    RUOLO: Il tuo ruolo è quello di assistere i clienti nella scelta dei prodotti più adatti alle loro esigenze, fornendo consulenza personalizzata e supporto post-vendita su informazioni che riguardano spedizioni, garanzie e resi.
    OBIETTIVO: Il tuo obiettivo è quello di aumentare le vendite e la soddisfazione del cliente, garantendo un'esperienza di acquisto unica e indimenticabile.
    TONO: Il tuo tono è professionale, cordiale e competente, in grado di instaurare un rapporto di fiducia con il cliente.
    
    ---

    Ensure that all parts are fully customized based on the provided information.
    Remember to write all in '{st.session_state['language']}' language."""

    user_prompt = f"""
    Create a custom prompt for a chatbot with the following information:
    Assistant Name: {info['nome_assistente']}
    Company Name: {info['nome_azienda']}
    Purpose: {info['scopo']}
    Objective: {info['obiettivo']}
    Personality: {info['personalita']}
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def generate_standard_prompt(info):
    openai.api_key = st.session_state['openai_key']
    system_prompt = f"""You are an expert in creating standard prompts for chatbots. 
    Your task is to customize a standard prompt template based on the given information.
    The output should strictly follow this structure:
    
    REGOLE: Rules for the chatbot interaction, including dont respond to sensitive topics, etc.
    IMMEDESIMAZIONE E APPARTENENZA AZIENDA: Always refer to the company as 'we' or 'us', and the user as 'you'.
    LUNGHEZZA MESSAGGI: Keep messages concise and to the point, avoiding long paragraphs.
    CONSULENZA & RAPPORTI DI LUNGO PERIODO: Provide advice and build long-term relationships with users.
    ---

    Example :
    REGOLE: Please avoid discussing sensitive topics such as politics, religion, or personal information. Always maintain a professional and respectful tone. If you encounter question about competitors, please redirect the user to our unique selling points about our company.
    IMMEDESIMAZIONE E APPARTENENZA AZIENDA: We are here to help you with any questions or concerns you may have. Always refer to us as 'we' or 'us' and to you as 'you'.
    LUNGHEZZA MESSAGGI: Keep your messages short and to the point to ensure clarity and understanding.
    CONSULENZA & RAPPORTI DI LUNGO PERIODO: We aim to provide you with the best advice and support to build a long-term relationship based on trust and reliability.

    ---

    Ensure that all parts are customized based on the provided information while maintaining the core structure. Scrivi come degli ordini.
    Remember to write all in '{st.session_state['language']}' language."""

    user_prompt = f"""
    Customize this standard prompt for a chatbot based on the following information:
    Company Name: {info['nome_azienda']}
    Personality: {info['personalita']}
    Purpose: {info['scopo']}
    Objective: {info['obiettivo']}
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def generate_faqs(content):
    openai.api_key = st.session_state['openai_key']
    faqs = {}
    
    system_prompt = f"""You are an expert in creating FAQs based on given content.
    Generate 10 relevant and insightful FAQ pairs in the following format:
    Q: [Question]
    A: [Concise Answer]
    
    Ensure that the questions and answers are directly related to the provided content.
     Remember to write all in '{st.session_state['language']}' language."""

    for title, text in content.items():
        user_prompt = f"Generate 10 FAQ pairs based on this content:\n\n{text}"
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        faqs[title] = response.choices[0].message.content
    
    return faqs

def get_table_download_link(text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="chatbot_prompt.txt">Download Prompt</a>'

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        if login():
            st.success(get_text("login_success"))
            st.experimental_rerun()
    else:
        st.write(get_text("welcome").format(st.session_state['username']))
        
        with st.form("chatbot_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_assistente = st.text_input(get_text("assistant_name"))
                nome_azienda = st.text_input(get_text("company_name"))
                scopo = st.selectbox(get_text("assistant_purpose"), get_text("purposes"))
                
                if scopo in ["Appointment Booking", "Prenotazione appuntamenti"]:
                    booking_url = st.text_input(get_text("booking_url"))
                
                obiettivo = st.text_area(get_text("objective"))
            
            with col2:
                personalita = st.selectbox(get_text("personality"), get_text("personalities"))
                url_principale = st.text_input(get_text("main_url"))
                url_contatti = st.text_input(get_text("contact_url"))
                altri_url = st.text_area(get_text("other_urls"))
            
            submitted = st.form_submit_button(get_text("generate_button"))
            
            if submitted:
                with st.status(get_text("processing"), expanded=True) as status:
                    urls = [url_principale, url_contatti] + altri_url.split('\n')
                    content = scrape_urls(urls, status)
                    
                    info = {
                        'nome_assistente': nome_assistente,
                        'nome_azienda': nome_azienda,
                        'scopo': scopo,
                        'obiettivo': obiettivo,
                        'personalita': personalita
                    }
                    
                    if scopo in ["Appointment Booking", "Prenotazione appuntamenti"]:
                        info['obiettivo'] += f" Lo scopo principale è far prenotare i potenziali utenti su questo link di prenotazione: {booking_url}"
                    
                    status.write(get_text("step_custom_prompt"))
                    custom_prompt = generate_custom_prompt(info)
                    time.sleep(1)
                    
                    status.write(get_text("step_standard_prompt"))
                    standard_prompt = generate_standard_prompt(info)
                    time.sleep(1)
                    
                    status.write(get_text("step_faqs"))
                    faqs = generate_faqs(content)
                    time.sleep(1)
                    
                    status.update(label=get_text("process_complete"), state="complete", expanded=False)
                
                # Visualizzazione dei risultati in expander e text area
                with st.expander(get_text("custom_prompt"), expanded=True):
                    st.text_area("Custom Prompt", value=custom_prompt, height=300)
                
                with st.expander(get_text("standard_prompt"), expanded=True):
                    st.text_area("Standard Prompt", value=standard_prompt, height=300)
                
                with st.expander(get_text("generated_faqs"), expanded=True):
                    for title, faq_content in faqs.items():
                        st.subheader(title)
                        st.text_area(f"FAQ - {title}", value=faq_content, height=200)
                
                # Creazione del testo completo per il download
                full_text = f"{custom_prompt}\n---\nRULE [:\n{standard_prompt}\n]\n---\nYOUR MAIN CONTEXT: [\n\n"
                for title, faq_content in faqs.items():
                    full_text += f"{title}\n\n{faq_content}\n\n"
                full_text += "]"
                
                # Pulsante di download
                st.markdown(get_table_download_link(full_text), unsafe_allow_html=True)
                
                # Editor longform per il prompt completo
                with st.expander("Edit Full Prompt", expanded=False):
                    edited_prompt = st.text_area("Full Prompt Editor", value=full_text, height=600)
                    st.markdown(get_table_download_link(edited_prompt), unsafe_allow_html=True)
main()