docker run -d --name tlgbotcore --restart unless-stopped -v ./logs:/app/logs:z -v ./data:/app/data:z -v ./cfg/config_tlg.py:/app/cfg/config_tlg.py:z py-tlgbotcore



