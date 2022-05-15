gcloud functions deploy gdi-demo \
--entry-point trigger \
--region australia-southeast1 \
--runtime python37 \
--trigger-bucket gdi-data-workloads-demo
