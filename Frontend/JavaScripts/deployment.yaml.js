const deploymentYaml = `
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-data-backend
  namespace: rlg
  labels:
    app: rlg-data-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rlg-data-backend
  template:
    metadata:
      labels:
        app: rlg-data-backend
    spec:
      containers:
        - name: backend-data
          image: rlg_data_backend:latest
          ports:
            - containerPort: 5000
          env:
            - name: DATABASE_URL
              value: postgresql://user:password@db-data:5432/rlg_data
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: jwt-secret-key
            - name: STRIPE_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: stripe-secret-key
            - name: REDIS_URL
              value: redis://redis:6379/0
            - name: SENTRY_DSN
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: sentry-dsn
            - name: ONLYFANS_API_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: onlyfans-api-key
            - name: STRIPCHAT_API_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: stripchat-api-key
            - name: SHEER_API_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: sheer-api-key
            - name: PORNHUB_API_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: pornhub-api-key
          volumeMounts:
            - name: db-data-volume
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: db-data-volume
          persistentVolumeClaim:
            claimName: rlg-data-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-fans-backend
  namespace: rlg
  labels:
    app: rlg-fans-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rlg-fans-backend
  template:
    metadata:
      labels:
        app: rlg-fans-backend
    spec:
      containers:
        - name: backend-fans
          image: rlg_fans_backend:latest
          ports:
            - containerPort: 5001
          env:
            - name: DATABASE_URL
              value: postgresql://user:password@db-fans:5433/rlg_fans
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: jwt-secret-key
            - name: STRIPE_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: stripe-secret-key
            - name: REDIS_URL
              value: redis://redis:6379/0
            - name: SENTRY_DSN
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: sentry-dsn
          volumeMounts:
            - name: db-fans-volume
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: db-fans-volume
          persistentVolumeClaim:
            claimName: rlg-fans-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-frontend
  namespace: rlg
  labels:
    app: rlg-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rlg-frontend
  template:
    metadata:
      labels:
        app: rlg-frontend
    spec:
      containers:
        - name: frontend
          image: rlg_frontend:latest
          ports:
            - containerPort: 80
          env:
            - name: BACKEND_DATA_URL
              value: http://rlg-data-backend:5000
            - name: BACKEND_FANS_URL
              value: http://rlg-fans-backend:5001
          volumeMounts:
            - name: frontend-volume
              mountPath: /usr/share/nginx/html
      volumes:
        - name: frontend-volume
          persistentVolumeClaim:
            claimName: rlg-frontend-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-collection-service
  namespace: rlg
  labels:
    app: data-collection-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-collection-service
  template:
    metadata:
      labels:
        app: data-collection-service
    spec:
      containers:
        - name: data-collection
          image: data_collection:latest
          env:
            - name: TWITTER_API_KEY
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: twitter-api-key
            - name: FACEBOOK_ACCESS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: facebook-access-token
            - name: REDIS_URL
              value: redis://redis:6379/0
          volumeMounts:
            - name: data-collection-volume
              mountPath: /data
      volumes:
        - name: data-collection-volume
          persistentVolumeClaim:
            claimName: rlg-data-collection-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-scheduler
  namespace: rlg
  labels:
    app: task-scheduler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: task-scheduler
  template:
    metadata:
      labels:
        app: task-scheduler
    spec:
      containers:
        - name: task-scheduler
          image: task_scheduler:latest
          env:
            - name: CELERY_BROKER_URL
              value: redis://redis:6379/0
            - name: CELERY_RESULT_BACKEND
              value: redis://redis:6379/0
            - name: REDIS_URL
              value: redis://redis:6379/0
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-monitoring
  namespace: rlg
  labels:
    app: rlg-monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rlg-monitoring
  template:
    metadata:
      labels:
        app: rlg-monitoring
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: prometheus-config
              mountPath: /etc/prometheus
      volumes:
        - name: prometheus-config
          configMap:
            name: prometheus-config
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-grafana
  namespace: rlg
  labels:
    app: rlg-grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rlg-grafana
  template:
    metadata:
      labels:
        app: rlg-grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:latest
          ports:
            - containerPort: 3000
          env:
            - name: GF_SECURITY_ADMIN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: rlg-secrets
                  key: grafana-admin-password
          volumeMounts:
            - name: grafana-storage
              mountPath: /var/lib/grafana
      volumes:
        - name: grafana-storage
          persistentVolumeClaim:
            claimName: rlg-grafana-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-redis
  namespace: rlg
  labels:
    app: rlg-redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rlg-redis
  template:
    metadata:
      labels:
        app: rlg-redis
    spec:
      containers:
        - name: redis
          image: redis:6
          ports:
            - containerPort: 6379
          volumeMounts:
            - name: redis-data
              mountPath: /data
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: rlg-redis-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-kafka
  namespace: rlg
  labels:
    app: rlg-kafka
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rlg-kafka
  template:
    metadata:
      labels:
        app: rlg-kafka
    spec:
      containers:
        - name: kafka
          image: wurstmeister/kafka:latest
          ports:
            - containerPort: 9093
          env:
            - name: KAFKA_ZOOKEEPER_CONNECT
              value: zookeeper:2181
            - name: KAFKA_ADVERTISED_LISTENER
              value: INSIDE://kafka:9093
            - name: KAFKA_LISTENER_SECURITY_PROTOCOL
              value: PLAINTEXT
          volumeMounts:
            - name: kafka-data
              mountPath: /var/lib/kafka/data
      volumes:
        - name: kafka-data
          persistentVolumeClaim:
            claimName: rlg-kafka-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rlg-zookeeper
  namespace: rlg
  labels:
    app: rlg-zookeeper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rlg-zookeeper
  template:
    metadata:
      labels:
        app: rlg-zookeeper
    spec:
      containers:
        - name: zookeeper
          image: wurstmeister/zookeeper:latest
          ports:
            - containerPort: 2181
          volumeMounts:
            - name: zookeeper-data
              mountPath: /data
      volumes:
        - name: zookeeper-data
          persistentVolumeClaim:
            claimName: rlg-zookeeper-pvc
`;

module.exports = deploymentYaml;
