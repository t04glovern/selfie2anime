# selfie2anime

## Components

### Image Handler

```bash
cd image-handler
serverless deploy
```

### Web

```bash
cd web
aws s3 sync public/ s3://selfie2anime.com --delete --acl public-read
```
