"""Scheduler Module - 定时任务调度"""
import logging
import sys
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import PUSH_INTERVAL_HOURS, LOG_LEVEL, LOG_FORMAT

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_news_radar():
    """运行新闻雷达任务"""
    logger.info("=" * 60)
    logger.info(f"🚀 AI News Radar started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    logger.info("=" * 60)
    
    try:
        # 导入 main 模块并执行
        import main
        main.run()
    except Exception as e:
        logger.error(f"News radar task failed: {e}", exc_info=True)
    
    logger.info("=" * 60)
    logger.info(f"🏁 AI News Radar finished at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    logger.info("=" * 60)


def start_scheduler():
    """启动定时调度器"""
    scheduler = BackgroundScheduler()
    
    # 添加每小时执行的任务
    scheduler.add_job(
        run_news_radar,
        IntervalTrigger(hours=PUSH_INTERVAL_HOURS),
        id='news_radar_job',
        name='AI News Radar',
        replace_existing=True,
        misfire_grace_time=300  # 允许 5 分钟的延迟执行
    )
    
    # 立即执行一次
    logger.info("🔄 Running initial fetch...")
    run_news_radar()
    
    # 启动调度器
    scheduler.start()
    logger.info(f"⏰ Scheduler started. Next run in {PUSH_INTERVAL_HOURS} hour(s).")
    logger.info("Press Ctrl+C to exit.")
    
    try:
        # 保持程序运行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("✓ Scheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
