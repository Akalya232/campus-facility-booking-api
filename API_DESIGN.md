# Campus Facility Booking API - Design

## Entities

### User
- id
- name
- email

### Facility
- id
- name
- location
- capacity

### Booking
- id
- user_id
- facility_id
- date
- start_time
- end_time
- purpose

## Relationships

- One User can create many Bookings.
- One Facility can have many Bookings.
- Each Booking belongs to one User.
- Each Booking belongs to one Facility.

## Endpoint Plan

### Users

#### POST /users
Success:
- 201 Created - User created successfully.

Errors:
- 400 Bad Request - Invalid user data.
- 422 Unprocessable Entity - Validation error.

#### GET /users/{user_id}
Success:
- 200 OK - User returned successfully.

Errors:
- 404 Not Found - User does not exist.


### Facilities

#### POST /facilities
Success:
- 201 Created - Facility created successfully.

Errors:
- 400 Bad Request - Invalid facility data.
- 422 Unprocessable Entity - Validation error.

#### GET /facilities
Success:
- 200 OK - List of facilities returned.


### Bookings

#### POST /bookings
Success:
- 201 Created - Booking created successfully.

Errors:
- 400 Bad Request - Invalid booking data.
- 404 Not Found - User or facility does not exist.
- 409 Conflict - Facility is already booked for the requested time.
- 422 Unprocessable Entity - Validation error.

#### GET /bookings
Success:
- 200 OK - List of bookings returned.


#### GET /bookings/{booking_id}
Success:
- 200 OK - Booking returned successfully.

Errors:
- 404 Not Found - Booking does not exist.


#### DELETE /bookings/{booking_id}
Success:
- 204 No Content - Booking cancelled successfully.

Errors:
- 404 Not Found - Booking does not exist.