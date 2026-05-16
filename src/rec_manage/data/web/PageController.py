"""
PageController.py
Flask route controller for rec_manage.
Author: Ethan Hageman
Version: 0.1
"""
from datetime import date
import os
import secrets

from flask import jsonify, render_template, request, session, redirect, url_for
from flask_classful import FlaskView, route
from src.rec_manage.data.objects.zone_check import zonecheck
from src.rec_manage.data.objects.SAL import save_and_load

UPLOAD_FOLDER = "src/rec_manage/static/uploads"


class PageController(FlaskView):
    route_base = "/"

    #helper methods

    def get_sal(self):
        #takes the business_id from the manager or employee signed in session
        #and populates the data with it, loading from the save and load class
        return save_and_load(session.get('business_id'))

    def _auth_required(self):
        # Verify that a business is authenticated in the session, return an error response if not authenticated
        # very helpful for finding deep rooted errors if the business id was not properly set.
        if 'business_id' not in session:
            return jsonify({"status": "error", "message": "Not authenticated"}), 401
        return None


    # Page routes

    @route('/')
    def index(self):
        # Render the public landing page.
        return render_template("index.html")

    @route('/signup', methods=["GET", "POST"])
    def signup(self):
        # Show the business sign-up form or create a new business on POST.
        if request.method == "GET":
            return render_template("business_sign_up.html")
        try:
            data = request.json
            manager_name = data.get("manager_name", "").strip()
            business_name = data.get("business_name", "").strip()
            address_str = data.get("address", "").strip()
            manager_password = data.get("password", "").strip()

            if not all([manager_name, business_name, address_str, manager_password]):
                return jsonify({"status": "error", "message": "Missing required fields"}), 400

            parts = address_str.split(",")
            if len(parts) != 2:
                return jsonify({"status": "error", "message": "Address must be in format 'lat,lng'"}), 400
            lat, lng = float(parts[0].strip()), float(parts[1].strip())

            sal = save_and_load()
            business_id = sal.create_business(business_name, lat, lng)
            manager_id = sal.add_manager(business_id, manager_name, manager_password, role="owner")
            session.update({
                'business_id': business_id,
                'manager_name': manager_name,
                'user_type': 'manager'
            })
            return jsonify({
                "status": "ok",
                "message": "Business created successfully",
                "business_id": business_id,
                "manager_id": manager_id,
                "redirect": url_for('PageController:map')
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @route('/employee_signup', methods=["GET", "POST"])
    def employee_signup(self):
        # Show the employee sign-up form or create an employee after invite code validation.
        if request.method == "GET":
            return render_template("employee_sign_up.html")
        try:
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            employee_password = request.form.get("password", "").strip()
            invite_code = request.form.get("invite_code", "").strip()

            if not all([first_name, last_name, employee_password, invite_code]):
                return jsonify({"status": "error", "message": "Missing required fields"}), 400

            sal = save_and_load()
            business_id = sal.redeem_invite_code(invite_code)
            if not business_id:
                return jsonify({"status": "error", "message": "Invalid or already used invite code"}), 400

            picture_path = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file.filename:
                    filename = f"{first_name}_{last_name}_{file.filename}"
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    picture_path = f"static/uploads/{filename}"

            sal = save_and_load(business_id)
            emp_id = sal.add_employee(first_name, last_name, employee_password, picture_path=picture_path)
            session.update({
                'business_id': business_id,
                'employee_id': emp_id,
                'employee_name': f"{first_name} {last_name}",
                'user_type': 'employee'
            })
            return jsonify({"status": "ok", "employee_id": emp_id, "redirect": url_for('PageController:employee_map')})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @route('/signin', methods=["GET", "POST"])
    def signin(self):
        # Show the sign-in form or authenticate a manager/employee on POST.
        if request.method == "GET":
            return render_template("sign_in.html")
        try:
            data = request.json
            name = data.get("manager_name", "").strip()
            password = data.get("password", "").strip()

            if not name or not password:
                return jsonify({"status": "error", "message": "Username and password are required"}), 400

            sal = save_and_load()

            manager = sal.authenticate_manager(name, password)
            if manager:
                session.update({'business_id': manager['business_id'], 'manager_name': manager['name'], 'user_type': 'manager'})
                return jsonify({"status": "ok", "redirect": url_for('PageController:map')})

            employee = sal.authenticate_employee(name, password)
            if employee:
                session.update({'business_id': employee['business_id'], 'employee_id': employee['employee_id'], 'employee_name': employee['name'], 'user_type': 'employee'})
                return jsonify({"status": "ok", "redirect": url_for('PageController:employee_map')})

            return jsonify({"status": "error", "message": "User not found"}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @route('/map/')
    def map(self):
        # Render the manager map page with employee and zone data.
        if 'business_id' not in session:
            return redirect(url_for('PageController:signin'))
        sal = self.get_sal()
        return render_template("map.html",
            employees=sal.load_employees(),
            zones=sal.load_zones(),
            org=sal.get_business_info()
        )

    @route('/employee_map')
    def employee_map(self):
        # Render the employee map page using the authenticated business.
        sal = self.get_sal()
        return render_template("employee_map.html", org=sal.get_business_info())

    # API actions

    @route("/zones", methods=["GET", "POST"])
    def zones(self):
        # Load zones or add a new zone for the authenticated business.
        auth = self._auth_required()
        if auth: return auth
        sal = self.get_sal()
        if request.method == "GET":
            return jsonify(sal.load_zones())
        try:
            zone_data = request.json
            zone_id = sal.add_zone(
                zone_data.get("label") or zone_data.get("name"),
                zone_data.get("color", "#3B8BD4"),
                zone_data.get("geojson", {})
            )
            return jsonify({"status": "ok", "id": zone_id})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @route("/employees", methods=["GET", "POST"])
    def employees(self):
        # List employees or create a new employee for the signed-in business.
        auth = self._auth_required()
        if auth: return auth
        sal = self.get_sal()
        if request.method == "GET":
            return jsonify(sal.load_employees())
        try:
            data = request.json
            first_name = data.get("first_name", "").strip()
            last_name = data.get("last_name", "").strip()
            if not first_name or not last_name:
                return jsonify({"status": "error", "message": "First name and last name are required"}), 400

            password = secrets.token_hex(4)
            emp_id = sal.add_employee(first_name, last_name, password)
            return jsonify({"status": "ok", "id": emp_id, "password": password})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @route("/employees/<int:employee_id>", methods=["DELETE"])
    def delete_employee(self, employee_id):
        # Delete an employee record for the authenticated business.
        auth = self._auth_required()
        if auth: return auth
        self.get_sal().delete_employee(employee_id)
        return jsonify({"status": "ok"})

    @route("/check_zone", methods=["POST"])
    def check_zone(self):
        # Validate a location against zones and optionally assign the employee to a shift.
        auth = self._auth_required()
        if auth: return auth
        data = request.json
        employee_name = data.get("employee_name")
        employee_id = data.get("employee_id")
        lat = data.get("lat")
        lng = data.get("lng")
        selected_time = data.get("selected_time")
        sal = self.get_sal()
        ZC = zonecheck()

        for zone in sal.load_zones():
            coordinates = zone.get("geojson", {}).get("geometry", {}).get("coordinates", [[]])[0]
            if not coordinates:
                continue
            if ZC.point_in_polygon(lat, lng, coordinates):
                response = {
                    "in_zone": True,
                    "employee": employee_name,
                    "zone_name": zone["name"],
                    "zone_id": zone["id"],
                    "zone_lat": sum(c[1] for c in coordinates) / len(coordinates),
                    "zone_lng": sum(c[0] for c in coordinates) / len(coordinates)
                }
                if employee_id and selected_time:
                    shift_date = data.get("shift_date") or date.today().isoformat()
                    assigned_id = sal.assign_employee_to_zone(
                        int(employee_id), int(zone["id"]), shift_date, selected_time
                    )
                    if assigned_id is None:
                        return jsonify({"status": "error", "message": "Employee already assigned for this time"}), 400
                    response.update({"assigned_id": assigned_id, "start_time": selected_time,})
                return jsonify(response)

        return jsonify({"in_zone": False}), 200

    @route("/schedule", methods=["GET"])
    def schedule(self):
        #API point for loading the schedule for a selected date
        auth = self._auth_required()
        if auth: return auth
        shift_date = request.args.get("date", date.today().isoformat())
        return jsonify(self.get_sal().load_schedule(shift_date))

    @route("/unassign/<int:assigned_id>", methods=["DELETE"])
    def unassign(self, assigned_id):
        #API point for unassigning an employee from a zone, deletes the slot assignment record for the given assigned_id
        auth = self._auth_required()
        if auth: return auth
        self.get_sal().delete_assignment(assigned_id)
        return jsonify({"status": "ok"})

    @route("/generate_invite", methods=["POST"])
    def generate_invite(self):
        #API point for generating a new invite code for the current business, returns the code for sharing with new employees
        auth = self._auth_required()
        if auth: return auth
        try:
            code = self.get_sal().generate_invite_code()
            return jsonify({"status": "ok", "invite_code": code})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500