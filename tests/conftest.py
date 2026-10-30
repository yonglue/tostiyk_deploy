import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.database import get_session
from app.deps import get_current_actor, Actor
from app import models  # noqa: F401  触发所有模型注册到 SQLModel.metadata


@pytest.fixture(name="session")
def session_fixture(tmp_path):
    """
    每个测试使用独立的文件型 SQLite（见 README「历史问题处理记录」#2）。

    不要用 `sqlite:///:memory:` + StaticPool：
    - `:memory:` 每个 connection 是独立实例，service 层多次 session.refresh 会丢数据
    - StaticPool 让所有线程共享同一条连接，并发请求抛 sqlite3.InterfaceError
    """
    db_file = tmp_path / "test_erp.db"
    test_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(test_engine)
    try:
        with Session(test_engine) as session:
            yield session
    finally:
        SQLModel.metadata.drop_all(test_engine)
        test_engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    # 覆盖鉴权：直接返回拥有所有权限的 super_admin
    def get_actor_override():
        return Actor(username="test_bot", role="super_admin", permissions=["*"])

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_actor] = get_actor_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
