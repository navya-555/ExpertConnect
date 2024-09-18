## ExpertConnect: A novel solution for instant and accurate profile matching
ExpertConnect leverages large language models and machine learning to match experts with interview boards based on candidates' skills and domains. By embedding profiles and calculating similarity scores, it delivers a scalable and precise solution for expert-candidate matching through an intuitive and visually appealing website.

## Installation

1. If you don’t have Python installed, install it [from Python.org](https://www.python.org/downloads/).

2. Clone this repository:

    ```bash
    git clone https://github.com/navya-555/ExpertConnect.git
    ```

3. Create a new virtual environment:

   - macOS:
     ```bash
     $ python -m venv venv
     $ . venv/bin/activate
     ```

   - Windows:
     ```cmd
     > python -m venv venv
     > .\venv\Scripts\activate
     ```

   - Linux:
      ```bash
      $ python -m venv venv
      $ source venv/bin/activate
      ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

6. Add your [API key](https://ai.google.dev/gemini-api/docs/api-key) to the newly created `.env` file or as an environment variable.
  
7. Run the application :<br>

   ```bash
    python app.py
    ```
   
You should now be able to access the app from your browser at the following URL: [http://127.0.0.1:5500](http://127.0.0.1:5500)!
