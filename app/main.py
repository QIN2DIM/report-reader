import sys

import httpx
import streamlit as st
from loguru import logger

# --- 日志配置 (Loguru) ---
# 移除默认的 Streamlit 日志处理器，使用 Loguru 全权接管
logger.remove()
# 添加一个标准错误输出，这在 Docker/Kubernetes 等容器化环境中是最佳实践
# 日志格式清晰，包含时间、级别、模块、函数和行号，便于调试
logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    ),
    colorize=True,
)

# --- 核心功能函数 ---


def fetch_markdown_content(url: str) -> str:
    """
    使用 httpx 从指定的 URL 获取 Markdown 文件内容。

    Args:
        url (str): Markdown 文件的公开 URL.

    Returns:
        str: 文件的文本内容.

    Raises:
        ValueError: 当网络请求失败或服务器返回非 200 状态码时抛出。
    """
    logger.info(f"开始从 URL 获取内容: {url}")
    # 使用 httpx.Client 并设置超时和允许重定向，这是生产环境的最佳实践
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url)
            # raise_for_status() 会对 4xx 和 5xx 状态码抛出 HTTPStatusError 异常
            response.raise_for_status()
            logger.success(f"成功获取内容, 状态码: {response.status_code}")
            # 明确使用 utf-8 解码，兼容中文等非 ASCII 字符
            return response.content.decode("utf-8")
    except httpx.HTTPStatusError as e:
        # 处理 HTTP 错误 (如 404 Not Found, 500 Server Error)
        error_message = (
            f"HTTP 错误 {e.response.status_code}: 无法在 {e.request.url} 找到文件或服务器出错。"
        )
        logger.error(error_message)
        raise ValueError(error_message) from e
    except httpx.RequestError as e:
        # 处理网络层面的错误 (如 DNS 解析失败, 连接超时)
        error_message = f"网络请求失败: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e
    except Exception as e:
        # 捕获其他未知异常
        error_message = f"发生未知错误: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# --- Streamlit 应用主逻辑 ---


def main():
    """
    Streamlit 应用的主入口函数。
    """
    # st.set_page_config 应该在应用的最开始调用一次
    st.set_page_config(page_title="Markdown URL Reader", layout="centered")

    logger.info("应用启动或页面刷新。")

    # 从 URL query string 中获取 "url" 参数
    # st.query_params 是 Streamlit 1.33+ 的现代用法，比 st.experimental_get_query_params() 更好
    query_params = st.query_params
    md_url = query_params.get("url")

    if md_url:
        # --- 场景1: URL 参数存在 ---
        logger.info(f"检测到 URL 参数: {md_url}")

        # 使用 st.spinner 提供加载中的友好提示
        with st.spinner(f"正在从 `{md_url}` 加载内容..."):
            try:
                # 调用核心函数获取内容
                markdown_content = fetch_markdown_content(md_url)

                # 渲染获取到的 Markdown 内容
                # st.markdown() 是 Streamlit 内置的渲染模块
                # unsafe_allow_html=True 允许 Markdown 中的原始 HTML 标签，对于复杂的 Markdown 很实用
                st.markdown(markdown_content, unsafe_allow_html=True)

                logger.success(f"成功渲染来自 {md_url} 的 Markdown。")

            except ValueError as e:
                # 如果 fetch_markdown_content 抛出异常，在这里捕获并显示错误信息
                st.error(
                    f"**加载失败**\n\n无法获取或渲染指定的 Markdown 文件。\n\n**错误详情:**\n`{e}`"
                )
                logger.warning(f"加载 URL {md_url} 失败: {e}")
    else:
        # --- 场景2: URL 参数不存在 ---
        # 显示欢迎和使用说明页面
        logger.info("未检测到 URL 参数，显示引导页面。")
        st.title("Markdown URL 阅读器 📖")
        st.subheader("通过 URL 参数动态加载并渲染一个公开的 Markdown 文件。")

        st.info(
            "**使用方法:**\n\n"
            "在当前页面的浏览器地址栏后方，添加 `?url=` 参数，并附上您想查看的 Markdown 文件的完整 URL。"
        )

        st.text("格式示例:")
        st.code("http://<your-streamlit-app>/?url=https://<path-to-your>/file.md", language="bash")

        st.markdown("---")

        st.subheader("点击下方链接查看一个示例:")
        # 提供一个可靠的、公开的 Markdown 文件作为示例
        example_url = "https://raw.githubusercontent.com/streamlit/streamlit/develop/README.md"

        # 动态生成指向自身的、带参数的 URL
        # st.page_link() 是新版 Streamlit 中创建内部导航链接的推荐方式，但对于动态 query 更简单的做法是直接构造 a 标签
        st.markdown(
            f'➡️ [加载 Streamlit 的官方 README.md]({st.get_option("server.baseUrlPath")}?url={example_url})'
        )


if __name__ == "__main__":
    main()
