from urllib.parse import urlparse

import gradio as gr
import requests

from settings import settings, THEME_DIR, LOG_DIR
from utils import init_log
from loguru import logger

init_log(
    runtime=LOG_DIR.joinpath("runtime.log"),
    error=LOG_DIR.joinpath("error.log"),
    serialize=LOG_DIR.joinpath("serialize.log"),
)


def fetch_content(url=None):
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
            file_extension = urlparse(url).path.split(".")[-1].lower()
            return content, file_extension
        except Exception as e:
            return f"获取内容时出错：{str(e)}", None
    else:
        return "请提供文件链接。", None


def create_ui():
    css_paths = [
        THEME_DIR.joinpath("phycat.css").resolve(),
        THEME_DIR.joinpath("phycat.user.css").resolve(),
    ]
    with gr.Blocks(css_paths=css_paths) as app:
        url_input = gr.Textbox(
            label="输入 URL", placeholder="https://example.com/document.md", visible=False
        )
        logger.debug(f"Input url: {url_input}")

        submit_button = gr.Button("加载", visible=False)

        content_display = gr.Markdown(label="文件内容", elem_classes="wrap-text markdown-body")

        def load_and_display_content(url):
            content, file_extension = fetch_content(url)
            return gr.Markdown(
                value=content,
                label="文件内容",
                elem_classes="wrap-text markdown-body",
                elem_id="write",
            )

        def load_from_url(request: gr.Request):
            url = request.query_params.get("url")
            if url:
                content_output = load_and_display_content(url)
                return content_output, gr.update(visible=False), gr.update(visible=False)
            else:
                return (
                    gr.Markdown(
                        value="请输入 URL", label="文件内容", elem_classes="wrap-text markdown-body"
                    ),
                    gr.update(visible=True),
                    gr.update(visible=True),
                )

        app.load(load_from_url, outputs=[content_display, url_input, submit_button])
        submit_button.click(load_and_display_content, inputs=url_input, outputs=[content_display])

    return app


def main():
    app = create_ui()
    app.launch(
        server_name="0.0.0.0", server_port=settings.SERVER_READER_PORT, show_error=True, share=True
    )


if __name__ == "__main__":
    main()
