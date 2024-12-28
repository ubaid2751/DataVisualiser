import pandas as pd
import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import styling

class DataVisualizer:
    def __init__(self):
        load_dotenv()
        self.upload_folder = "./tmp"
        self.model_name = "llama3-70b-8192"
        self.groq_api_key = ""
        self.create_upload_folder()
        self.model = None
        self.prompt = self.create_prompt_template()

    def create_upload_folder(self):
        os.makedirs(self.upload_folder, exist_ok=True)
        for filename in os.listdir(self.upload_folder):
            if len(os.listdir(self.upload_folder)) > 5:
                os.remove(os.path.join(self.upload_folder, filename))

    def set_groq_api_key(self, api_key):
        self.groq_api_key = api_key
        self.model = ChatGroq(api_key=self.groq_api_key, model=self.model_name)

    def create_prompt_template(self):
        return ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a data visualization expert and use your favourite graphing library Plotly only. Suppose, that "
                "the data is provided as a ./tmp/{filename}.csv file. Here are the first 5 rows of the data set: {data} "
                "Follow these styling guidelines while creating the graph:\n{styling_instructions}\n"
                "Follow the user's indications when creating the graph."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def get_fig_from_code(self, code):
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

    def create_graph(self, csv_string, user_input, filename, style):
        response = self.prompt | self.model
        response = response.stream(
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
                fig = self.get_fig_from_code(code_block)
                return fig, result_op
            except Exception as e:
                st.error(f"Error processing the code block: {e}")
                return None, result_op
        else:
            st.error("No valid code block found in the response.")
            return None, result_op

    def process_file_upload(self, uploaded_file):
        file_path = os.path.join(self.upload_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = pd.read_csv(uploaded_file, encoding="utf-8")
        csv_string = df.head().to_string(index=False)
        return df, csv_string, file_path

class StreamlitApp:
    def __init__(self):
        self.visualizer = DataVisualizer()
        self.df = None
        self.csv_string = ""
        self.saved_file_path = None

    def render_sidebar(self):
        groq_api_key = st.sidebar.text_input("Enter Groq API key: ", type='password')
        if groq_api_key:
            self.visualizer.set_groq_api_key(groq_api_key)

    def render_main_app(self):
        st.title("✨ Data Visualizer ✨")

        data = st.file_uploader('', type=['csv'])
        if data is not None:
            self.df, self.csv_string, self.saved_file_path = self.visualizer.process_file_upload(data)
            st.dataframe(self.df.head(10))

        user_input = st.text_input("Provide a query to create visualizations from your dataset.", "Create a correlation map of all numeric features.")

        if st.button("🎨 Generate Visualization"):
            if self.saved_file_path is not None:
                with st.spinner("✨ Creating your masterpiece..."):
                    style = styling.get_styling_instructions(user_input)
                    fig, result_op = self.visualizer.create_graph(self.csv_string, user_input, self.saved_file_path, style)

                    if fig:
                        st.success("Visualization created successfully!")
                        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                    else:
                        st.error("No valid visualization code was generated.")
                    st.markdown(f"{result_op}", unsafe_allow_html=True)
            else:
                st.warning("Please upload a CSV file first.")

if __name__ == "__main__":
    app = StreamlitApp()
    app.render_sidebar()
    app.render_main_app()