from flask import Blueprint, request, jsonify, session
from db import SessionLocal
from models.personal_record import PersonalRecord
from datetime import date

personal_records_bp = Blueprint("personal_records", __name__)


@personal_records_bp.route("/api/personal_records", methods=["GET"])
def get_personal_records():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    db = SessionLocal()
    try:
        records = db.query(PersonalRecord).filter(
            PersonalRecord.user_id == user_id
        ).order_by(PersonalRecord.achieved_on.desc()).all()
        return jsonify([{
            "id": r.id,
            "exercise": r.exercise,
            "value": float(r.value),
            "unit": r.unit,
            "achieved_on": r.achieved_on.isoformat() if r.achieved_on else None,
            "notes": r.notes
        } for r in records])
    finally:
        db.close()


@personal_records_bp.route("/api/personal_records", methods=["POST"])
def add_personal_record():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    exercise = data.get("exercise", "").strip()
    value = data.get("value")
    unit = data.get("unit", "")
    achieved_on_str = data.get("achieved_on")
    notes = data.get("notes", "")
    if not exercise or value is None:
        return jsonify({"error": "exercise and value are required"}), 400
    try:
        value = float(value)
    except (TypeError, ValueError):
        return jsonify({"error": "value must be a number"}), 400
    achieved_on = date.fromisoformat(achieved_on_str) if achieved_on_str else date.today()
    db = SessionLocal()
    try:
        pr = PersonalRecord(
            user_id=user_id,
            exercise=exercise,
            value=value,
            unit=unit,
            achieved_on=achieved_on,
            notes=notes
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        return jsonify({
            "id": pr.id,
            "exercise": pr.exercise,
            "value": float(pr.value),
            "unit": pr.unit,
            "achieved_on": pr.achieved_on.isoformat() if pr.achieved_on else None,
            "notes": pr.notes
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@personal_records_bp.route("/api/personal_records/<int:record_id>", methods=["DELETE"])
def delete_personal_record(record_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    db = SessionLocal()
    try:
        pr = db.query(PersonalRecord).filter(
            PersonalRecord.id == record_id,
            PersonalRecord.user_id == user_id
        ).first()
        if not pr:
            return jsonify({"error": "Record not found"}), 404
        db.delete(pr)
        db.commit()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
