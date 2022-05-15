docker build -t gcr.io/lizzie-sandbox-310723/gdi-demo .

docker push gcr.io/lizzie-sandbox-310723/gdi-demo

gcloud run deploy gdi-demo-cloud-run \
    --image gcr.io/lizzie-sandbox-310723/gdi-demo \
    --region australia-southeast1 \
	--platform=managed