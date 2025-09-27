"""
Notification module for the 3-month high tracker
Handles various alerting mechanisms
"""
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import requests


class NotificationManager:
    """
    Handles notifications for the 3-month high tracker
    """
    
    def __init__(self, config: Dict):
        """
        Initialize notification manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_dir = Path(config.get('data_dir', 'data/'))
        self.data_dir.mkdir(exist_ok=True)
        # Calculate the time period description based on days
        days = config.get('price_history_days', 90)
        if days >= 365:
            self.time_period_desc = f"{days//365} Year{'s' if days//365 > 1 else ''}"
        elif days >= 30:
            self.time_period_desc = f"{days//30} Month{'s' if days//30 > 1 else ''}"
        else:
            self.time_period_desc = f"{days} Day{'s' if days > 1 else ''}"
    
    def _create_alert_message(self, alert: Dict, format_type: str = "default") -> str:
        """
        Create a standardized alert message based on the alert data and format type.
        
        Args:
            alert: Alert information dictionary
            format_type: Format type ('default', 'email', 'console', 'discord', 'telegram')
            
        Returns:
            Formatted alert message string
        """
        base_message = {
            'header': f"{self.time_period_desc} High Drop Alert",
            'exchange': alert['exchange'],
            'symbol': alert['symbol'],
            'current_price': f"${alert['current_price']:.4f}",
            'high_price': f"${alert['three_month_high']:.4f}",
            'drop_percentage': f"{alert['drop_percentage']:.2f}%",
            'high_timestamp': alert['high_timestamp'],
            'alert_time': alert['timestamp']
        }
        
        # Format for different notification types
        if format_type == "console":
            return (
                f"🚨 {base_message['header']} 🚨\n"
                f"Exchange: {base_message['exchange']}\n"
                f"Symbol: {base_message['symbol']}\n"
                f"Current Price: {base_message['current_price']}\n"
                f"{self.time_period_desc} High: {base_message['high_price']}\n"
                f"Drop: {base_message['drop_percentage']}\n"
                f"High Timestamp: {base_message['high_timestamp']}\n"
                f"Alert Time: {base_message['alert_time']}"
            )
        elif format_type == "email":
            return (
                f"🚨 {base_message['header']} 🚨\n\n"
                f"Exchange: {base_message['exchange']}\n"
                f"Symbol: {base_message['symbol']}\n"
                f"Current Price: {base_message['current_price']}\n"
                f"{self.time_period_desc} High: {base_message['high_price']}\n"
                f"Drop: {base_message['drop_percentage']}\n"
                f"High Timestamp: {base_message['high_timestamp']}\n"
                f"Alert Time: {base_message['alert_time']}"
            )
        elif format_type == "telegram":
            return (
                f"🚨 *{base_message['header']}* 🚨\n\n"
                f"*Symbol:* {base_message['symbol']}\n"
                f"*Exchange:* {base_message['exchange']}\n"
                f"*Current Price:* {base_message['current_price']}\n"
                f"*{self.time_period_desc} High:* {base_message['high_price']}\n"
                f"*Drop:* {base_message['drop_percentage']}\n"
                f"*High Time:* {base_message['high_timestamp']}\n"
                f"*Alert Time:* {base_message['alert_time']}"
            )
        else:  # default format
            return (
                f"🚨 {base_message['header']} 🚨\n"
                f"Exchange: {base_message['exchange']}\n"
                f"Symbol: {base_message['symbol']}\n"
                f"Current Price: {base_message['current_price']}\n"
                f"{self.time_period_desc} High: {base_message['high_price']}\n"
                f"Drop: {base_message['drop_percentage']}\n"
                f"High Timestamp: {base_message['high_timestamp']}\n"
                f"Alert Time: {base_message['alert_time']}"
            )
    
    def send_console_alert(self, alert: Dict):
        """
        Send alert to console
        
        Args:
            alert: Alert information dictionary
        """
        message = self._create_alert_message(alert, "console")
        logger.warning(message)
    
    def send_file_alert(self, alert: Dict):
        """
        Write alert to a log file
        
        Args:
            alert: Alert information dictionary
        """
        alerts_file = self.data_dir / "price_drop_alerts.json"
        
        # Read existing alerts
        existing_alerts = []
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r') as f:
                    existing_alerts = json.load(f)
            except Exception:
                existing_alerts = []
        
        # Add new alert
        existing_alerts.append(alert)
        
        # Write back to file (keeping only last 100 alerts to prevent file bloat)
        with open(alerts_file, 'w') as f:
            json.dump(existing_alerts[-100:], f, indent=2)
    
    def send_email_alert(self, alert: Dict):
        """
        Send alert via email
        
        Args:
            alert: Alert information dictionary
        """
        email_config = self.config.get('email', {})
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port', 587)
        sender_email = email_config.get('sender_email')
        sender_password = email_config.get('sender_password')
        recipient_emails = email_config.get('recipients', [])
        
        if not smtp_server or not sender_email or not sender_password or not recipient_emails:
            logger.warning("Email configuration is incomplete, skipping email alert")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipient_emails)
            msg['Subject'] = f"{self.time_period_desc} High Drop Alert: {alert['symbol']}"
            
            # Create message body using the shared template
            body = self._create_alert_message(alert, "email")
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            text = msg.as_string()
            server.sendmail(sender_email, recipient_emails, text)
            server.quit()
            
            logger.info(f"Email alert sent to {recipient_emails}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def send_discord_alert(self, alert: Dict):
        """
        Send alert to Discord webhook
        
        Args:
            alert: Alert information dictionary
        """
        webhook_url = self.config.get('discord_webhook_url')
        
        if not webhook_url:
            logger.warning("Discord webhook URL not configured, skipping Discord alert")
            return
        
        try:
            # Format the message as a Discord embed
            # Use the base alert data from the template function
            base_message = {
                'header': f"{self.time_period_desc} High Drop Alert",
                'exchange': alert['exchange'],
                'symbol': alert['symbol'],
                'current_price': f"${alert['current_price']:.4f}",
                'high_price': f"${alert['three_month_high']:.4f}",
                'drop_percentage': f"{alert['drop_percentage']:.2f}%",
                'high_timestamp': alert['high_timestamp'],
                'alert_time': alert['timestamp']
            }
            
            embed = {
                "title": f"🚨 {base_message['header']}: {base_message['symbol']}",
                "color": 15158332,  # Red color
                "fields": [
                    {"name": "Exchange", "value": base_message['exchange'], "inline": True},
                    {"name": "Current Price", "value": base_message['current_price'], "inline": True},
                    {"name": f"{self.time_period_desc} High", "value": base_message['high_price'], "inline": True},
                    {"name": "Drop Percentage", "value": base_message['drop_percentage'], "inline": True},
                    {"name": "High Timestamp", "value": base_message['high_timestamp'], "inline": True},
                    {"name": "Alert Time", "value": base_message['alert_time'], "inline": True}
                ]
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Discord alert sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
    
    def send_telegram_alert(self, alert: Dict):
        """
        Send alert via Telegram bot
        
        Args:
            alert: Alert information dictionary
        """
        bot_token = self.config.get('telegram_bot_token')
        chat_id = self.config.get('telegram_chat_id')
        
        if not bot_token or not chat_id:
            logger.warning("Telegram bot token or chat ID not configured, skipping Telegram alert")
            return
        
        try:
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            # Use the shared template for Telegram format
            message = self._create_alert_message(alert, "telegram")
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(telegram_url, data=payload)
            response.raise_for_status()
            
            logger.info("Telegram alert sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    
    def process_alert(self, alert: Dict):
        """
        Process an alert based on the configured notification method
        
        Args:
            alert: Alert information dictionary
        """
        notification_methods = self.config.get('notification_methods', ['console'])
        
        for method in notification_methods:
            try:
                if method == 'console':
                    self.send_console_alert(alert)
                elif method == 'file':
                    self.send_file_alert(alert)
                elif method == 'email':
                    self.send_email_alert(alert)
                elif method == 'discord':
                    self.send_discord_alert(alert)
                elif method == 'telegram':
                    self.send_telegram_alert(alert)
                else:
                    logger.warning(f"Unknown notification method: {method}")
            except Exception as e:
                logger.error(f"Error sending notification via {method}: {e}")