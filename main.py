import gemini_api
import expanded
import merge
import gigachat_api
import merge_gigachat

def main(API_KEY=None):
    # gemini_api.run()
    gigachat_api.run(API_KEY=API_KEY)
    expanded.run()
    # merge.run()
    merge_gigachat.run()


if __name__ == "__main__":
    main()