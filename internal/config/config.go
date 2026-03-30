package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	Port          int
	FetchTimeout  time.Duration
	TLSSkipVerify bool
}

func Load() Config {
	port := 31313
	if v := os.Getenv("SERVER_READER_PORT"); v != "" {
		if p, err := strconv.Atoi(v); err == nil {
			port = p
		}
	}

	timeout := 30 * time.Second
	if v := os.Getenv("FETCH_TIMEOUT"); v != "" {
		if t, err := strconv.Atoi(v); err == nil {
			timeout = time.Duration(t) * time.Second
		}
	}

	tlsSkip := true
	if v := os.Getenv("TLS_SKIP_VERIFY"); v == "false" {
		tlsSkip = false
	}

	return Config{
		Port:          port,
		FetchTimeout:  timeout,
		TLSSkipVerify: tlsSkip,
	}
}
