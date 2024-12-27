from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

import pandas as pd
import os 
import re
import streamlit as st 
from dotenv import load_dotenv
import styling

load_dotenv()
        
with st.sidebar:
    GROQ_API_KEY = st.text_input("Enter Groq api key: ", type='password')
MODEL_NAME = "llama3-70b-8192"
UPLOAD_FOLDER = "./tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

for filename in os.listdir(UPLOAD_FOLDER):
    if len(os.listdir(UPLOAD_FOLDER)) > 5:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))

model = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a data visualization expert and use your favourite graphing library Plotly only. Suppose, that "
            "the data is provided as a ./tmp/{filename}.csv file. Here are the first 5 rows of the data set: {data} "
            "Follow these styling guidelines while creating the graph:\n{styling_instructions}\n"
            "Follow the user's indications when creating the graph."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | model

def get_fig_from_code(code):
    local_env = {}
    try:
        cleaned_code = re.sub(r'\bfig\.show\(\)', '', code)
        exec(cleaned_code, {}, local_env)
        fig = local_env.get('fig')
        if isinstance(fig, dict) or hasattr(fig, 'to_plotly_json'):
            return fig
        else:
            raise ValueError("The generated code did not produce a valid Plotly Figure.")
    except Exception as e:
        st.error(f"Error executing generated code: {e}")
        return e

def create_graph(csv_string, user_input, filename, style):
    response = chain.stream(
        {
            "messages": [HumanMessage(content=user_input)],
            "filename": filename,
            "data": csv_string,
            "styling_instructions": style
        }
    )
    result_op = ""
    for chunk in response:
        print(chunk.content, end='', flush=True)
        result_op += chunk.content
    
    code_block = re.search(r'```(?:[Pp]ython)?(.*?)```', result_op, re.DOTALL)
    if code_block:
        code_block = code_block.group(1).strip()
        try:
            fig = get_fig_from_code(code_block)
            return fig, result_op
        except Exception as e:
            st.error(f"Error processing the code block: {e}")
            return None, result_op
    else:
        st.error("No valid code block found in the response.")
        return None, result_op

st.title("✨ Data Visualizer ✨")

df = None
df_5_rows = None
csv_string = ""
saved_file_path = None

data = st.file_uploader('', type=['csv'])
if data is not None:
    saved_file_path = os.path.join(UPLOAD_FOLDER, data.name)
    
    with open(saved_file_path, "wb") as f:
        f.write(data.getbuffer())
    
    df = pd.read_csv(data, encoding="utf-8")
    df_5_rows = df.head()
    csv_string = df_5_rows.to_string(index=False)
    st.dataframe(df.head(10))

user_input = st.text_input("Provide a query to create visualizations from your dataset.", "Create a correlation map of all numeric features.")

if st.button("🎨 Generate Visualization"):
    if saved_file_path is not None:
        fig = None
        with st.spinner("✨ Creating your masterpiece..."):
            style = styling.get_styling_instructions(user_input) 
            fig, result_op = create_graph(csv_string, user_input, saved_file_path, style)

            if fig:
                st.success("Visualization created successfully!")
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
            else:
                st.error("No valid visualization code was generated.")
            st.markdown(f"{result_op}", unsafe_allow_html=True)
    else:
        st.warning("Please upload a CSV file first.")