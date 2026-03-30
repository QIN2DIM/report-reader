# Stage 1: Build
FROM golang:1.26.1-trixie AS builder

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /report-reader .

# Stage 2: Runtime
FROM alpine:3.21

RUN apk --no-cache add ca-certificates

COPY --from=builder /report-reader /report-reader

EXPOSE 31313

ENTRYPOINT ["/report-reader"]
