# importing streamlit, enviroment variable and os bridger 
import os
import streamlit as st
#from dotenv import load_dotenv
# importing lanagchain and ai capabilities 
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from pypdf import PdfReader

from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

#The Expert Trimmer
from langchain_core.messages import trim_messages

#The Database Persistence Tracker
from langchain_community.chat_message_histories import SQLChatMessageHistory
# sql creation alchemy 
from sqlalchemy import create_engine

# audio recorder 
from audio_recorder_streamlit import audio_recorder


# security and key vault 
#load_dotenv()

# variables 
if "login_details" not in st.session_state:
    st.session_state.login_details = {"user_name":" ", "user_password":" "}

if "user_background" not in st.session_state:
    st.session_state.user_background=" "

if "xy" not in st.session_state:
    st.session_state["xy"]=" "

if "user_goal_skill" not in st.session_state:
    st.session_state.user_goal_skil=" "
if "main_llm" not in st.session_state:
    st.session_state.main_llm=" "
if "mic_key" not in st.session_state:
    st.session_state.mic_key=0
if "experience_level2" not in st.session_state:
    st.session_state.experience_level2=None
if "coach_tone" not in st.session_state:
    st.session_state.coach_tone=None



p=" "
v1=" " 
v2=" "

# welocme and identification 
st.title("AI CAREER COACH")

st.caption("This generative AI application helps an Electrical engineer transition into AI engineer")
# form switch contlrol using streamlit session_state 
if "form1_submitted" not in st.session_state and "from2_submitted" not in st.session_state:
    st.session_state.form1_submitted= False 
    st.session_state.form2_submitted= False 

if not st.session_state.form1_submitted and not st.session_state.form2_submitted:
    with st.form(key="profile_form"):
        name = st.text_input("How Should I Call You(do not enter your real details)").strip()
        password = st.text_input("Enter Password").strip()
        t=0
        while True:
            if name and password: # if the fields are filled, then we collect the details 
                st.session_state.login_details["user_name"]=name 
                st.session_state.login_details["user_passward"]=password
                break 
            if t<1:
                st.warning("do not allow any fields blank")
                t+=1
                break 
        col1,col2 = st.columns([4,1])
        with col1:
            st.form_submit_button("submit")
        with col2:
            if st.form_submit_button("Next"):
                if name and password:
                    st.session_state.form1_submitted=False 
                    st.session_state.form2_submitted=True
                    st.rerun()
    


if not st.session_state.form1_submitted and st.session_state.form2_submitted:
    with st.form(key="Background"):
        current_background= st.selectbox("What is your current background in electrical engineering /You can choose to upload your CV instead",[" ","Graduate Student","Professional in power generatation","professional in renewable energy ","professional in power grid management","electronic system design","Education(Teaching,Lecturing)"]).strip()
        
        uploadedcv_pdf= st.file_uploader("Uplaod CV instead", type=["pdf"])# file upload widjet
       
        col1,col2 = st.columns([4,1]) # creating space for horizontal side by side button( ratio f 4/5 to 1/5)
        with col1:
            if st.form_submit_button("return"):
                st.session_state.form1_submitted=False 
                st.session_state.form2_submitted=False 
                st.rerun()
            
        with col2:
            form_submit2=st.form_submit_button(" Next")
        if form_submit2:
            if uploadedcv_pdf is not None:
                 with st.spinner("extracting text from your CV"):
                        #reading the pdf file 
                        read_pdf=PdfReader(uploadedcv_pdf)
                        # looping  through the pdf to extract text 
                        CVText=" "
                        for page in read_pdf.pages:
                            CVText += page.extract_text() + "\n"
                        # saving the text cv into streamlit session state memory 
                        #st.session_state.usersTextcv=CVText
                        st.session_state.xy=CVText
                        st.session_state.form1_submitted=True
                        st.session_state.form2_submitted=False 
                        st.rerun() 
            if current_background:
                st.session_state.user_background= current_background
                st.session_state.form1_submitted=True
                st.session_state.form2_submitted=False 
                st.rerun() 
            
            else:
                 if not current_background:
                    if uploadedcv_pdf is None:
                        st.warning("please choose a background or enter your CV")
y1= st.session_state.xy
#st.write(st.session_state.xy)

if st.session_state.form1_submitted and not st.session_state.form2_submitted:
    with st.form(key="Enter Your Goals"):
        user_goal=st.selectbox("Enter your Goals: What skills will you like to acquire in this domain",["Build ML models ","Build AI Application "," Become an AI professional"," Build AI based Business automations"," Develop foundation AI models(build, train, test ) "," Deep learning expert ","ML Engineer","AI automation Engineer"])
        col1,col2 = st.columns([4,1])
        with col1:
            form_submitt3=st.form_submit_button("return")
            if form_submitt3:
                st.session_state.form1_submitted=False 
                st.session_state.form2_submitted=True
                st.rerun()

        with col2:
            form_submit33 = st.form_submit_button("Submit")
            if form_submit33:
                st.session_state.user_goal_skill=user_goal
                st.session_state.form1_submitted=True
                st.session_state.form2_submitted=True 
                st.rerun()

if st.session_state.form1_submitted and st.session_state.form2_submitted:
    # combining user password and user and password to generate their session_id
    
    audio_bytes=None 
    session_id=st.session_state.login_details["user_name"] + st.session_state.login_details["user_password"]
    # memory reset function
    def memory_reset(session_id):

        def get_session_history(session_id):
            return SQLChatMessageHistory(
                session_id=session_id,
                connection="sqlite:///ai_career_Coach_history.db"#engine 
            )
        # access the user's history, and delete it
        user_history=get_session_history(session_id)
        user_history.clear()
        # clear any streamlit user screen messages 
        if "messages" in st.session_state:
            st.session_state.messages=[]
            st.rerun()

    
    # the main interaction window
    main_llm=" "
    experience_level2=" " 
    coach_tone=None 
    ai_tone=" "  # a variable
    #model_holder={"OpenAI_gpt-4o-mini":"ChatOpenAI(model="gpt-4o-mini",temperature=0.3)","Anthropic_claude sonnet":"claude-sonnet-4-20250514","ollama":"http://localhost:11434","gemini_flash":"ChatGoogleGenerativeAI(model="gemini-3.5-flash",temperature=0.7)"}
    st.subheader("welcome to your ai engineer  journey")
    # creating the sidebar 
    with st.sidebar:
        #dynamic mic key 
        current_key=f"active_mic{st.session_state.mic_key}"
        model_choice=st.selectbox("choose the AI Brain you like to use", ["OpenAI_gpt-4o-mini","Anthropic_claude sonnet","ollama","gemini_flash"])
        experience_level=st.text_input("enter your level of experience in years").strip()
        ai_tone=st.selectbox("choose the tone you will like the Coach to use",["Formal","casual"])
        coaching_stage=st.selectbox("Choose your coaching stage",["Road-map stage","Job Interview Stage","Profiling stage","Job Search/Salary negotiation stage"])
        #creating columns for two button 
        col1,col2 = st.columns([2,3]) 
        with col1:

            # submit botton 
            if st.button("SUBMIT"):
                #model selector unit 
                match model_choice:
                    case "OpenAI_gpt-4o-mini":
                        st.session_state.main_llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.3,streaming=True)
                    case "Anthropic_claude sonnet":
                        st.session_state.main_llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.3,streaming=True)
                    case "ollama":
                        st.session_state.main_llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.3,streaming=True)
                        #st.session_state.main_llm=ChatOllama( model="gemma4:12b",temperature=0.7)
                        
                    case "gemini_flash":
                        st.session_state.main_llm=ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=1.0,max_retries=10, streaming=True)
                    case _:
                        st.write("pick a model")
                if experience_level:
                    st.session_state.experience_level2=experience_level
                else:
                    st.warning(" do not allow this field empty")
                if ai_tone:
                    st.session_state.coach_tone= ai_tone
                else:
                    st.warning(" do not allow this field empty")

            with col2:
                if st.button("New Session"):
                    memory_reset(session_id)
        # audio recorder 
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#aaaaaa",
            key=current_key
            )
            


try:

    mainn_llm = st.session_state.main_llm 
    # use an llm to summarice and extract background from pdf
    # use the user name and password to pull up user  from chat history SQL data base or put user and new user in the base if the user is not already in 

    # using the llm to  summarize and extract the user's background from their text-based CV
    def userCV_summarized(y1):
        llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)
        prompt_blueprint1 = """you are a text editing expert capable of summarizing and contextualising a text.
            your resposibility here is to summarize curriculum vitaes(CV) into a complete background representation of the person so the
            information can be further used by another language model to propose a study road map for the person in becoming an AI engineer.
            so, summarize this curriculum vitae(CV): {user_curriculumVitae}"""

        prompt1=PromptTemplate.from_template(prompt_blueprint1)
        summarizer_chain=prompt1|llm|StrOutputParser()
        summary=summarizer_chain.invoke({"user_curriculumVitae":y1})
        return summary 
    
    
    # Creating all the necessary prompts that will be further used to dynamically multiple chains 
    #1 the road map prompt and chain 
    prompt_blueprint1="""You are an AI career coach whose responsibility is to review a user's backgound
        and provide a detailed study outline including if necessary(courses, certifications, 
        training programs, universisty programs, bootcamps and many more that you can find, 
        detailing everything out how it affect the journey ), that can  assist elctrical engineers properly  transition to AI engineers.
         You have to  carefully review the user's backgound to provide this study outline using their provided details on
        their Curriculum vitae({cv}), and or their professional background({user_profession}).
        
        Warning: you should judge the user's CV to find out if they are and electrical engineer or have an electrical background, if you find out 
        they are not an electrical engineer or do not have an electrical backgorund, tell them politely that you are to focus only on coaching
        electrical engineers transition AI engineers and that based on their CV you cannot be of help to them, then do not generate any study outline.

        THE USER'S GOAL 
        Also take into considaration the goal/skill({user_skill}) that the user which to acquire so as to better fine-tune the study outline.
        Make sure to really propose the study ouline depending on the user's background to make sure  the user can cope with the studies.
        If there is something you think the user lacks, make sure you ask them to go and study it as prerequisite so as to better aline them selves with the stusy program or outline that you will propose.
        """
    road_map_prompt=ChatPromptTemplate.from_template(prompt_blueprint1)
    road_map_chain= road_map_prompt|mainn_llm|StrOutputParser()
    road_map_result=road_map_chain.invoke({"cv":st.session_state.xy,"user_profession":st.session_state.user_background,"user_skill":st.session_state.user_goal_skill})
    #st.write(road_map_result)
    # The chatprompt to always recieve the various prompts 

    #THE MOCK PROMPT AND CHAIN 
    #-
    mock_prompt_blueprint="""You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer.Right now, you have as a task to genereate possible job interview questions
        and how the user should answer them, following this sudy outline{road_map_resultPH} ."""
    mock_prompt=ChatPromptTemplate.from_template(mock_prompt_blueprint)
    #-the mock chain 
    mock_chain=mock_prompt|mainn_llm|StrOutputParser()
    mock_result = mock_chain.invoke({"road_map_resultPH":road_map_result})

    #THE CV AND PROFILING PROMPT AND CHAIN 
    #-profiling prompt 
    profiling_prompt_blueprint = """ You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer.Right now, you have as a task to help/guide  the user develop a proper profile such as a  CV(curriculum vitae), a good
        linkedIn profile or other reputable social media platforms profilling for the user, considering that the user has completely gone through  this mock job interview questions stage such as this example {mock_resultPH} """
    profiling_prompt=ChatPromptTemplate.from_template(profiling_prompt_blueprint)
    #-the profiling chain 
    profiling_chain=profiling_prompt|mainn_llm|StrOutputParser()
    profiling_result=profiling_chain.invoke({"mock_resultPH":mock_result})

    # THE JOB SEARCHA AND SALARY NEGOTIATION PROMPT AND CHAIN
    #-job and salary negotiation prompt 
    job_salary_promptBlueprint="""You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer.Right now, you have as a task to guide the user on how to search for jobs and also guide the user on
        how to negotiate their salary, taking into considaration that the user has gone through this profile coaching stage{profiling_resultPH}.
        """
    job_salary_prompt=ChatPromptTemplate.from_template(job_salary_promptBlueprint)
    #-job and salary chain 
    job_salary_chain=job_salary_prompt|mainn_llm|StrOutputParser()
    job_salary_result= job_salary_chain.invoke({"profiling_resultPH":profiling_result})

    #list of chat_prompts
        #-1 chat prompt on road map 
    chat_prompt=ChatPromptTemplate.from_messages([
        ("system","""you are an AI career coach whose responsibilty is to help an electrical engineer switch or transition into an 
        artificial intelligence(AI) following a well structured provided study outline.
        This is the provided study outline:{road_map_resultPH} 
        You should help the user understand the study outline better as the ask their questions
        Warning : 
        -you should judge the user's CV({cv}) to find out if they are and electrical engineer or have an electrical background, if you find out 
        they are not an electrical engineer or do not have an electrical backgorund, tell them politely that you are to focus only on coaching
        electrical engineers transition to AI engineers and nothing else, and   that based on their CV you cannot be of help to them, then do not generate any study outline.
        -if a question asked by a user is completely out of line with what your given responsibility is , tell the user  politely that you are to focus only on your  responsiblity or  role as designed for you
        -so make sure not to go out of your sphere of responsibilty, but make sure to be politely. 
        - if asked questions about other stage or stages  which is the profilling stages, job search and salary negotiation  stages tell the user that right now you are supposed to fucuss on 
        coaching the user on the study ouline  and that they can move to other  stage to have such discussions.
        - welcome the user in the beginning and make the user understand that in this interaction you are to focus only on your task right now
        Experience: Note that the user has {current_experience} years of experience in their current discipline of electrical engineering
        Coaching tone: the user will like you to use a {coaching_tone} tone in coaching them"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{input}")])
        
        #-2 chat prompt on mock job preparation
    chat_prompt2=ChatPromptTemplate.from_messages([
        ("system","""You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer.Right now, you have as a task to prepare the user for job interviews by generating  possible mock job interview questions
        and guide the user on how to answer them, taking into considaration that the user has completely studied the following study outline{road_map_resultPH}. 
        
        Warning : 
        -if a question asked by the user is completely out of line with your given task right now, tell the user  politely that you are to focus only on your task right now, which is to which is to coach the user on job interview and generate possible job interview mock questions 
        and help them how to answer the questions.
        -so make sure not to  go out of your sphere of task right now, but make sure to be politely.
        - if asked questions about other stage or stages  which is the study ouline stage,profilling stages, job search and salary negotiation  stages tell the user that right now you are supposed to fucuss on 
        mock job interview and that they can move to previews stage to have such discussions
        Experience: Note that the user has {current_experience} years of experience in their current discipline fo electical engineering
        Coaching tone: the user will like you to use a {coaching_tone} tone in coaching them
        
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{input}")])

    #-3 chat prompt on CV and profiling
    chat_prompt3 =ChatPromptTemplate.from_messages([
        ("system","""You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer.Right now, you have as a task to guide the user on how to develope a good profile for them selves, like for example a good CV(curriculum vitae), a linkedIn profile or other social media profillng technique.
        , taking into considaration that the user has completely gone through the mock job interview questions stage.
        
        Example profile: you can also learn from this example profile,{profiling_resultPH} but do more  better.
        Warning : 
        - do not forget to ask the user if the have example projects that they have carried out, so that you can guide them how to make these projects part of their profiling and make their profile even stronger.
        -if a question asked by the user is completely out of line with your given task right now, tell the user  politely that you are to focus only on your task right now, which is to guide the user develop a good profile for them selves 
        in preparation for the job search stage.
        -so make sure not to  go out of your sphere of task right now, but make sure to be politely.
        - if asked questions about the other stage or stages, which are the study ouline, job mock interview questions, job search and salary negotiation  stages, tell the user that right now you are supposed to fucuss on 
        coaching the user on profiling and that they can move to previews or next  stage/stages  to have such discussions 
        Experience: Note that the user has {current_experience} years of experience in their current discipline of electricla engineering 
        Coaching tone: the user will like you to use a {coaching_tone} tone in coaching them"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{input}")])
    
    chat_prompt4=ChatPromptTemplate.from_messages([
        ("system","""You are an AI career coach whose responsibilty is to help an electrical enginer transition or
        switch into an artificial intelligence engineer(AI engineer).Right now, you have as a task to guide the user on how to search for jobs, intrenship opportunities and guide the user also on how to negotiate salary. provide links to job sites, internship sites  that you think can be of good help to the user.
        , taking into considaration that the user has completely gone through the stage that coaches the user on how to develop a good profile. 
        Job search and salary negotiation example: you can also learn from this job search and salary negotiation example,{job_salary_resultPH} but do more  better.
        Warning : 
        - you can ask the user if they have a company in mind that they will like to work in so that you can find out if they have the type of job opportunities or internships for that can be good for the user.
        -if a question asked by the user is completely out of line with your given task right now, tell the user  politely that you are to focus only on your task right now, which is to guide the user on how to search jobs, internships and better negotiate salary   
        
        -so make sure not to  go out of your sphere of task right now, but make sure to be politely.
        - if asked questions about other stage or stages, which are the study ouline, job mock interview questions, profilling stages, tell the user that right now you are supposed to fucuss on 
        coaching the user on jobs, internships search and salary negotiation, that they can move to other  stage/stages  to have such discussions
        Experience: Note that the user has {current_experience} years of experience in their current discipline of electrical engineering  
        Coaching tone: the user will like you to use a {coaching_tone} tone in coaching them """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{input}")])





    # the CHATBOT'S BODY 
    def chat_bot_body(dynamic_prompt,session_id):
        user_query=None 
        voice_query=None
        transcription_flag=False 
        # the main llm 
        session_id=session_id
        
        # 2. Setup the Token Trimmer (Protects your budget)
        message_trimmer = trim_messages(
            max_tokens=400,                  # Caps input context window size
            strategy="last",                 # begin from the last chats 
            token_counter=mainn_llm,               
            include_system=True            # Protects our core agent identity
            )
    
        prompt=dynamic_prompt # the body prompt 
        # connecting the trimmer to the prompt and esatablishing the chain
        
        core_chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: message_trimmer.invoke(x["chat_history"])
                )
                | prompt
                | mainn_llm
                )
        

    # the chat database connection engine. this creates the pipline to the sql database 
    #engine = create_engine("sqlite:///ai_career_Coach_history.db")
    #function that go get the chat history from the database for a particular session_id
        def get_session_history(session_id):
            return SQLChatMessageHistory(
                session_id=session_id,
                connection="sqlite:///ai_career_Coach_history.db"#engine 
            )
        p=get_session_history(session_id)
                #return p

        # 6. Wrap everything together
        final_production_chain = RunnableWithMessageHistory(
            core_chain,
            get_session_history, #  Handed over to the database file!
            input_messages_key="input",
            history_messages_key="chat_history"
            )
        # Pull logs directly from SQLite database to render on user screen reload
        
    
        history_ledger = get_session_history(session_id)
        for msg in history_ledger.messages:
            st.chat_message(msg.type).write(msg.content) # smart UI message displayer(dynamically picking the right visual style(User vs AI ))
        
        # Processing the audio if recorded by the user
        # client 
        client = OpenAI()
        if audio_bytes:
            with st.spinner("Transcribing your audio with Whisper..."):
                try:

                    # 1. Save the bytes to a temporary audio file format Whisper expects
                    temp_filename = "temp_audio.wav"
                    with open(temp_filename, "wb") as f:
                        f.write(audio_bytes)
                    # 2. Open and pass the file handle straight to OpenAI's Whisper model
                    with open(temp_filename, "rb") as audio_file:
                        transcription = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file,
                        language="en"
                        )
                    # 3. Clean up the temp file from disk
                    os.remove(temp_filename)
                    # 4. Save the plain text transcript to route into  chain
                    voice_query = transcription.text
                    voice_query.strip()
                    st.sidebar.success(f"Transcribed: \"{voice_query}\"")
                    transcription_flag=True 
                except Exception as e:
                    st.sidebar.error(f"Audio processing error: {e}")
        
        
        
        text_query=st.chat_input("Ask SARA, or Type hello to Begin...")
        user_query = voice_query if voice_query else text_query

        if user_query:
            
            st.chat_message("human").write(user_query)
    
            config = {"configurable": {"session_id": session_id}}
    
            with st.chat_message("ai"):
                def get_stream():
                    #pulling from the chain 
                    for chunk in final_production_chain.stream(
                        {"input": user_query,"road_map_resultPH":road_map_result,"history":p,"mock_resultPH":mock_result,"profiling_resultPH":profiling_result,"job_salary_resultPH":job_salary_result,"cv":st.session_state.xy,"current_experience":st.session_state.experience_level2,"coaching_tone":st.session_state.coach_tone},config):
                        #checking the data structure, we will use these two python built-in function used to ispect data (hasattr() and isinstance())
                        if isinstance(chunk, dict) and "answer" in chunk:
                            yield chunk["answer"]
                        elif hasattr(chunk, "content"):
                            yield chunk.content
                        else:
                            yield str(chunk)
                response=st.write_stream(get_stream())

                #with st.spinner("Optimizing data streams..."):
                    #response = final_production_chain.invoke({"input": user_query,"road_map_resultPH":road_map_result,"history":p,"mock_resultPH":mock_result,"profiling_resultPH":profiling_result,"job_salary_resultPH":job_salary_result,"cv":st.session_state.xy},config)
                #st.write(response.content)
                if transcription_flag:
                    st.session_state.mic_key+=1 

       
    
    #st.write(" great new journey")
    if coaching_stage=="Road-map stage":
        chat_bot_body(chat_prompt,session_id)
    if coaching_stage=="Job Interview Stage":
        chat_bot_body(chat_prompt2,session_id)
    if coaching_stage=="Profiling stage":
        chat_bot_body(chat_prompt3,session_id)
    if coaching_stage=="Job Search/Salary negotiation stage":
        chat_bot_body(chat_prompt4,session_id)
except Exception as err:
    st.warning("Fill in the fields") 



    
            




        
    



















    






    

