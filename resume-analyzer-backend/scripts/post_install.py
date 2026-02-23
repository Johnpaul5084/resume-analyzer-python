import spacy
import os

def main():
    print("Downloading spaCy model 'en_core_web_sm'...")
    try:
        spacy.cli.download("en_core_web_sm")
        print("Successfully downloaded 'en_core_web_sm'.")
    except Exception as e:
        print(f"Error downloading spaCy model: {e}")

if __name__ == "__main__":
    main()
