![Python](https://img.shields.io/badge/python-3.12-blue.svg)  [![Tests](https://github.com/SanjinDedic/code_hint/actions/workflows/test.yml/badge.svg)](https://github.com/SanjinDedic/code_hint/actions/workflows/test.yml)  [![codecov](https://codecov.io/gh/SanjinDedic/code_hint/graph/badge.svg?token=PWUU4GJSOD)](https://codecov.io/gh/SanjinDedic/code_hint)


# Code Hint API

The Code Hint API is a FastAPI-based application that does the following:
- validates user requests for code hints before sending them to OpenAI API by ensuring only valid code is sent
- validates OpenAI API responses based on avoiding internal contradicitons and content warnings.
- records all validated requests and responses for research purposes


# Known issues:
- `is_this_python` function gives no false negatives but it is still not reliable in passing Python code with errors as Python
- All validation should ideally happen in `models.py` but testing is mocked and I dont have enough data on actual validator performance.
- Once validation is sorted endpoints should be refactored for better error handling and neater API response parsing.


## Deployment

To deploy the Code Hint API, follow these steps:

1. **Get a server**: Set up a server or hosting environment to deploy the application. This can be a cloud-based server, a virtual private server (VPS), or a local machine.

2. **Clone the repository**: Clone the project repository to your server using the following command:
   ```
   git clone <repository_url>
   ```

3. **Create a virtual environment**: Navigate to the project directory and create a virtual environment to isolate the project dependencies. Run the following commands:
   ```
   cd code_hint
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**: Install the project dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

5. **Set up the OpenAI API key**: Obtain an API key from OpenAI. Create a `.env` file in the project root directory and add the following line:
   ```
   OPENAI_API_KEY=<your_api_key>
   ```
   Replace `<your_api_key>` with your actual OpenAI API key.

6. **Test the application**: Before running the application, you can test it by running the `run_headless.py` script. This script allows you to select a code snippet and analyze it using the API. Run the following command:
   ```
   python run_headless.py
   ```
   Follow the prompts to select a code snippet and view the analysis results.

7. **Run the application**: To start the API server, run the following command:
   ```
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
   This will start the server and make it accessible at `http://localhost:8000`.

## API Endpoints

The Code Hint API provides the following endpoints:

- `GET /`: Returns a simple "Hello World" message to confirm that the API is running.
- `POST /get_code_hints`: Accepts a JSON payload containing a code snippet and returns the analysis results, including hints, error information, and content warnings.

## Project Structure

The project has the following structure:

- `api.py`: The main FastAPI application file that defines the API endpoints and handles the requests.
- `models.py`: Defines the SQLModel models for the `CodeSnippet` and `CodeHint` tables in the database.
- `database.py`: Contains the database configuration and utility functions for creating tables and saving data.
- `utils.py`: Provides utility functions for code analysis, such as checking if the code is valid Python.
- `run_headless.py`: A script for testing the API by submitting code snippets and displaying the analysis results.

## Dependencies

The Code Hint API relies on the following dependencies:

- FastAPI: A modern, fast (high-performance) Python web framework for building APIs.
- SQLModel: A library for defining SQL databases and models using Python classes.
- OpenAI API: An AI platform that provides language models for code analysis and generating hints.

Make sure to install the required dependencies listed in the `requirements.txt` file.

## Contributing

If you would like to contribute to the Code Hint API project, please follow the standard GitHub workflow:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

We appreciate your contributions and feedback!

## License

The Code Hint API is open-source and released under the [MIT License](LICENSE).
