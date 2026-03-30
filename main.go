package main

import (
	"embed"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"

	"github.com/qin2dim/report-reader/internal/config"
	"github.com/qin2dim/report-reader/internal/fetcher"
	"github.com/qin2dim/report-reader/internal/renderer"
)

//go:embed templates/*.html
var templateFS embed.FS

//go:embed static/phycat.css
var phycatCSS string

var (
	cfg            config.Config
	contentFetcher *fetcher.Fetcher
	mdRenderer     *renderer.Renderer
	tmplDocument   *template.Template
	tmplForm       *template.Template
)

type documentData struct {
	CSS     template.CSS
	Content template.HTML
}

func init() {
	cfg = config.Load()
	contentFetcher = fetcher.New(cfg.FetchTimeout, cfg.TLSSkipVerify)
	mdRenderer = renderer.New()

	tmplDocument = template.Must(template.ParseFS(templateFS, "templates/document.html"))
	tmplForm = template.Must(template.ParseFS(templateFS, "templates/form.html"))
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}

	urlParam := strings.TrimSpace(r.URL.Query().Get("url"))

	if urlParam == "" {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		tmplForm.Execute(w, nil)
		return
	}

	// Validate URL scheme
	if !strings.HasPrefix(urlParam, "http://") && !strings.HasPrefix(urlParam, "https://") {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		renderError(w, "获取内容时出错：仅支持 http/https 协议")
		return
	}

	markdown, err := contentFetcher.Fetch(urlParam)
	if err != nil {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		renderError(w, err.Error())
		return
	}

	htmlContent, err := mdRenderer.Render(markdown)
	if err != nil {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		renderError(w, "渲染内容时出错："+err.Error())
		return
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmplDocument.Execute(w, documentData{
		CSS:     template.CSS(phycatCSS),
		Content: template.HTML(htmlContent),
	})
}

func renderError(w http.ResponseWriter, msg string) {
	tmplDocument.Execute(w, documentData{
		CSS:     template.CSS(phycatCSS),
		Content: template.HTML("<p>" + template.HTMLEscapeString(msg) + "</p>"),
	})
}

func main() {
	http.HandleFunc("/", handleRoot)

	addr := fmt.Sprintf("0.0.0.0:%d", cfg.Port)
	log.Printf("Report Reader starting on %s", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
