package fetcher

import (
	"crypto/tls"
	"fmt"
	"io"
	"net/http"
	"time"
)

type Fetcher struct {
	client *http.Client
}

func New(timeout time.Duration, tlsSkipVerify bool) *Fetcher {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: tlsSkipVerify},
	}
	return &Fetcher{
		client: &http.Client{
			Timeout:   timeout,
			Transport: transport,
		},
	}
}

func (f *Fetcher) Fetch(url string) (string, error) {
	resp, err := f.client.Get(url)
	if err != nil {
		return "", fmt.Errorf("获取内容时出错：%v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("获取内容时出错：HTTP %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("获取内容时出错：%v", err)
	}
	return string(body), nil
}
