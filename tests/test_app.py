"""HTTP regression checks for administrative CRUD workflows."""

from crud_app.config import Settings
from tests.conftest import csrf_from


def test_authentication_required(client, headers):
    response = client.get("/tables/department")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"].startswith("Basic")
    assert client.get("/tables/department", headers=headers).status_code == 200
    invalid = {"Authorization": "Basic YWRtaW46d3Jvbmc="}
    assert client.get("/tables/department", headers=invalid).status_code == 401


def test_navigation_and_legacy_read_aliases(client, headers):
    assert client.get("/", headers=headers).status_code == 302
    assert client.get("/department", headers=headers).status_code == 302
    assert client.get("/relation/course_gives_skill", headers=headers).status_code == 302
    assert client.get("/tables/__class__", headers=headers).status_code == 404
    assert client.get("/arbitrary", headers=headers).status_code == 404


def test_create_edit_delete_and_csrf(client, app, headers):
    new = client.get("/tables/department/new", headers=headers)
    token = csrf_from(new)
    create_url = "/tables/department/create"
    data = {"department_id": "2", "department_name": "Research", "budget": "23.5"}
    assert client.post(create_url, headers=headers, data=data).status_code == 400
    created = client.post(create_url, headers=headers, data={**data, "csrf_token": token})
    assert created.status_code == 303
    repo = app.extensions["table_repository"]
    records, has_more = repo.list_records("department", page=2)
    assert not has_more
    assert records[0]["department_name"] == "Research"
    key = repo.record_key("department", records[0])
    edit_url = f"/tables/department/edit/{key}"
    assert client.get(edit_url, headers=headers).status_code == 200
    edited = client.post(
        edit_url, headers=headers,
        data={"department_name": "Updated", "budget": "30", "csrf_token": token},
    )
    assert edited.status_code == 303
    assert repo.get_record("department", key)["department_name"] == "Updated"
    deleted = client.post(
        f"/tables/department/delete/{key}", headers=headers, data={"csrf_token": token}
    )
    assert deleted.status_code == 303
    assert client.get(edit_url, headers=headers).status_code == 404


def test_unexpected_fields_and_invalid_types(client, headers):
    token = csrf_from(client.get("/tables/department/new", headers=headers))
    data = {"department_id": "2", "department_name": "Good", "budget": "100"}
    assert client.post(
        "/tables/department/create", headers=headers,
        data={**data, "evil": "true", "csrf_token": token},
    ).status_code == 400
    assert client.post(
        "/tables/department/create", headers=headers,
        data={**data, "budget": "invalid", "csrf_token": token},
    ).status_code == 400
    assert client.post(
        "/tables/department/create", headers=headers,
        data={**data, "department_name": "", "csrf_token": token},
    ).status_code == 400


def test_duplicate_primary_key_returns_conflict(client, headers):
    token = csrf_from(client.get("/tables/department/new", headers=headers))
    response = client.post(
        "/tables/department/create", headers=headers,
        data={
            "department_id": "1",
            "department_name": "Another",
            "budget": "100",
            "csrf_token": token,
        },
    )
    assert response.status_code == 409
    assert b"UNIQUE constraint" not in response.data


def test_composite_primary_key_and_no_get_delete(client, app, headers):
    repo = app.extensions["table_repository"]
    record = repo.list_records("course_gives_skill")[0][0]
    key = repo.record_key("course_gives_skill", record)
    assert client.get(
        f"/tables/course_gives_skill/delete/{key}", headers=headers
    ).status_code == 405
    assert repo.get_record("course_gives_skill", key)["skill_id"] == 20
    form = client.get(f"/tables/course_gives_skill/edit/{key}", headers=headers)
    token = csrf_from(form)
    assert client.post(
        f"/tables/course_gives_skill/edit/{key}", headers=headers,
        data={"csrf_token": token},
    ).status_code == 303
    assert client.post(
        f"/tables/course_gives_skill/delete/{key}", headers=headers,
        data={"csrf_token": token},
    ).status_code == 303


def test_invalid_identity_and_escaped_html(client, app, headers):
    assert client.get(
        "/tables/department/edit/not-valid!", headers=headers
    ).status_code == 400
    token = csrf_from(client.get("/tables/department/new", headers=headers))
    payload = "<script>alert(1)</script>"
    response = client.post(
        "/tables/department/create", headers=headers,
        data={
            "department_id": "3", "department_name": payload,
            "budget": "12", "csrf_token": token,
        },
    )
    assert response.status_code == 303
    page = client.get("/tables/department?page=2", headers=headers)
    assert b"&lt;script&gt;" in page.data
    assert payload.encode() not in page.data


def test_pagination_and_invalid_page(client, headers):
    assert client.get("/tables/department?page=0", headers=headers).status_code == 400
    assert client.get("/tables/department?page=10001", headers=headers).status_code == 400
    assert client.get("/tables/department", headers=headers).status_code == 200


def test_environment_configuration():
    values = {
        "DATABASE_URL": "sqlite://",
        "CRUD_ADMIN_PASSWORD": "strong-password",
        "FLASK_SECRET_KEY": "a" * 32,
        "PAGE_SIZE": "12",
        "COOKIE_SECURE": "true",
    }
    config = Settings.from_env(values)
    assert config.cookie_secure
    assert config.page_size == 12
