# app/api/routers/queue_status.py
"""
큐 상태 모니터링 API
"""
from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse
from services.lightweight_queue_manager import get_queue_manager
import json

router = APIRouter()

def generate_status_html(status_info):
    """큐 상태 정보를 HTML로 변환"""
    queue_stats = status_info.get("queue_stats", {})
    processing_count = status_info.get("processing_count", {})
    resource_usage = status_info.get("resource_usage", {})
    limits = status_info.get("limits", {})
    is_running = status_info.get("is_running", False)
    
    # 리소스 사용량 색상 결정
    memory_color = "red" if resource_usage.get("memory_percent", 0) > 80 else "orange" if resource_usage.get("memory_percent", 0) > 60 else "green"
    cpu_color = "red" if resource_usage.get("cpu_percent", 0) > 80 else "orange" if resource_usage.get("cpu_percent", 0) > 60 else "green"
    
    # 서비스별 통계 테이블 생성
    service_rows = ""
    for service_type, stats in queue_stats.items():
        pending = stats.get("pending", 0)
        processing = stats.get("processing", 0)
        completed = stats.get("completed", 0)
        failed = stats.get("failed", 0)
        
        max_concurrent = limits.get(service_type, {}).get("max_concurrent", "N/A")
        max_queue_size = limits.get(service_type, {}).get("max_queue_size", "N/A")
        current_processing = processing_count.get(service_type, 0)
        
        # 처리율 계산
        total_processed = completed + failed
        success_rate = (completed / total_processed * 100) if total_processed > 0 else 0
        
        service_rows += f"""
        <tr>
            <td>{service_type}</td>
            <td><span class="badge pending">{pending}</span></td>
            <td><span class="badge processing">{current_processing}/{max_concurrent}</span></td>
            <td><span class="badge completed">{completed}</span></td>
            <td><span class="badge failed">{failed}</span></td>
            <td>{success_rate:.1f}%</td>
            <td>{max_queue_size}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Queue Status Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 30px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }}
            .header h1 {{
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .status-indicator {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                background: {'#28a745' if is_running else '#dc3545'};
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                text-align: center;
            }}
            .metric-card h3 {{
                color: #495057;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-label {{
                color: #6c757d;
                font-size: 0.9em;
            }}
            .table-container {{
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                margin-bottom: 20px;
            }}
            .table-header {{
                background: #495057;
                color: white;
                padding: 15px;
                font-size: 1.2em;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #dee2e6;
            }}
            th {{
                background: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }}
            .badge {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.85em;
                font-weight: bold;
                color: white;
            }}
            .badge.pending {{ background: #ffc107; color: #212529; }}
            .badge.processing {{ background: #007bff; }}
            .badge.completed {{ background: #28a745; }}
            .badge.failed {{ background: #dc3545; }}
            .refresh-info {{
                text-align: center;
                color: #6c757d;
                font-size: 0.9em;
                margin-top: 20px;
            }}
            .auto-refresh {{
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                margin: 10px;
            }}
            .auto-refresh:hover {{
                background: #0056b3;
            }}
        </style>
        <script>
            let autoRefresh = false;
            let refreshInterval;
            
            function toggleAutoRefresh() {{
                const button = document.getElementById('refreshBtn');
                if (autoRefresh) {{
                    clearInterval(refreshInterval);
                    autoRefresh = false;
                    button.textContent = '자동 새로고침 시작';
                    button.style.background = '#007bff';
                }} else {{
                    refreshInterval = setInterval(() => {{
                        window.location.reload();
                    }}, 5000);
                    autoRefresh = true;
                    button.textContent = '자동 새로고침 중지';
                    button.style.background = '#dc3545';
                }}
            }}
            
            function refreshNow() {{
                window.location.reload();
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Queue Status Dashboard</h1>
                <div class="status-indicator">
                    {"🟢 시스템 실행중" if is_running else "🔴 시스템 중지"}
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>메모리 사용률</h3>
                    <div class="metric-value" style="color: {memory_color}">
                        {resource_usage.get('memory_percent', 0):.1f}%
                    </div>
                    <div class="metric-label">임계점: {resource_usage.get('memory_threshold', 0)}%</div>
                </div>
                
                <div class="metric-card">
                    <h3>CPU 사용률</h3>
                    <div class="metric-value" style="color: {cpu_color}">
                        {resource_usage.get('cpu_percent', 0):.1f}%
                    </div>
                    <div class="metric-label">임계점: {resource_usage.get('cpu_threshold', 0)}%</div>
                </div>
                
                <div class="metric-card">
                    <h3>총 완료 작업</h3>
                    <div class="metric-value" style="color: #28a745">
                        {sum(stats.get('completed', 0) for stats in queue_stats.values())}
                    </div>
                    <div class="metric-label">전체 서비스</div>
                </div>
                
                <div class="metric-card">
                    <h3>총 실패 작업</h3>
                    <div class="metric-value" style="color: #dc3545">
                        {sum(stats.get('failed', 0) for stats in queue_stats.values())}
                    </div>
                    <div class="metric-label">전체 서비스</div>
                </div>
            </div>
            
            <div class="table-container">
                <div class="table-header">📊 서비스별 큐 상태</div>
                <table>
                    <thead>
                        <tr>
                            <th>서비스</th>
                            <th>대기중</th>
                            <th>처리중</th>
                            <th>완료</th>
                            <th>실패</th>
                            <th>성공률</th>
                            <th>최대 큐 크기</th>
                        </tr>
                    </thead>
                    <tbody>
                        {service_rows}
                    </tbody>
                </table>
            </div>
            
            <div style="text-align: center;">
                <button class="auto-refresh" onclick="refreshNow()">지금 새로고침</button>
                <button class="auto-refresh" id="refreshBtn" onclick="toggleAutoRefresh()">자동 새로고침 시작</button>
            </div>
            
            <div class="refresh-info">
                <p>💡 이 페이지는 실시간 큐 상태를 보여줍니다.</p>
                <p>마지막 업데이트: {status_info.get('timestamp', 'N/A')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@router.get(
    "/queue/status",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    tags=["Queue"],
    summary="큐 상태 조회",
    description="현재 큐 상태와 리소스 사용량을 HTML 페이지로 조회합니다.",
)
async def get_queue_status():
    """
    큐 상태 조회 HTML 페이지
    - 각 서비스별 큐 통계
    - 현재 처리 중인 작업 수
    - 시스템 리소스 사용량
    """
    queue_manager = get_queue_manager()
    status_info = await queue_manager.get_status()
    
    # HTML 템플릿 생성
    html_content = generate_status_html(status_info)
    return HTMLResponse(content=html_content)

@router.get(
    "/queue/status/json",
    status_code=status.HTTP_200_OK,
    tags=["Queue"],
    summary="큐 상태 조회 (JSON)",
    description="현재 큐 상태와 리소스 사용량을 JSON으로 조회합니다.",
)
async def get_queue_status_json():
    """
    큐 상태 조회 JSON API
    - 각 서비스별 큐 통계
    - 현재 처리 중인 작업 수
    - 시스템 리소스 사용량
    """
    queue_manager = get_queue_manager()
    return await queue_manager.get_status()

@router.get(
    "/queue/health",
    status_code=status.HTTP_200_OK,
    tags=["Queue"],
    summary="큐 시스템 헬스체크",
    description="큐 시스템의 동작 상태를 확인합니다.",
)
async def queue_health_check():
    """큐 시스템 헬스체크"""
    queue_manager = get_queue_manager()
    
    try:
        status_info = await queue_manager.get_status()
        is_healthy = status_info["is_running"]
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "is_running": is_healthy,
            "message": "Queue system is operational" if is_healthy else "Queue system is not running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "is_running": False,
            "message": f"Queue system error: {str(e)}"
        }