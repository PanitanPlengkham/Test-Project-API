""" Testing the Reservation API endpoint for the World Class Government group"""
import unittest
import requests

HOST = "https://wcg-apis.herokuapp.com"
DATABASE_URL = HOST + "/citizen"
URL = HOST + "/reservation"
URL_registration = HOST + "/registration"
FEEDBACK = {
    'success_reservation': 'reservation success!',
    'success_registration': 'registration success!',
    'missing_attribute': 'reservation failed: missing some attribute',
    'reserved': 'reservation failed: there is already a reservation for this citizen',
    'invalid_citizen_id': 'reservation failed: invalid citizen ID',
    'not_registered': 'reservation failed: citizen ID is not registered',
    'invalid_vaccine_name': 'report failed: invalid vaccine name'
}


class ReservationTest(unittest.TestCase):
    """
    Unit tests for Reservation API for the website wcg-apis.herokuapp.com

    @author Panitan Plengkham
    """

    def setUp(self):
        # delete that citizen if that citizen already exist
        requests.delete(DATABASE_URL, data=self.create_citizen_reservation_info())

        # default info to make a registration
        self.citizen_registration = self.create_citizen_info()

        # default info to make a reservation
        self.citizen_reservation = self.create_citizen_reservation_info()

        # missing some attributes
        self.missing_attribute = [
            self.create_citizen_reservation_info(citizen_id=""),
            self.create_citizen_reservation_info(site_name="")
        ]

        # citizen_id is not the number of exact 13 digits
        self.invalid_citizen_id = [
            self.create_citizen_reservation_info(citizen_id="123"),  # 3 digits
            self.create_citizen_reservation_info(citizen_id="12345678901234567890"),  # 20 digits
            self.create_citizen_reservation_info(citizen_id="1abc2bcd3"),  # contain alphabets
            self.create_citizen_reservation_info(citizen_id="112233.44")  # contain float
        ]

        # invalid vaccine name
        self.invalid_vaccine_name = [
            self.create_citizen_reservation_info(vaccine_name="123"),   # contain integer
            self.create_citizen_reservation_info(vaccine_name="Vacacaca"),  # not the available vaccines
        ]

    def create_citizen_info(
            self,
            citizen_id="1103900076232",
            firstname="Panitan",
            lastname="Plengkham",
            birthdate="09 Feb 2001",
            occupation="Student",
            address="357/3 Namuang rd. 25000"):
        """Return new dict of the registration API requested attributes.

        Args:
            citizen_id (str, optional): Identity Number for the citizen of Thailand, default is "1103900076232"
            firstname (str, optional): Firstname of the citizen, default is "Panitan"
            lastname (str, optional): Lastname of the citizen, default is "Plengkham"
            birthdate (str, optional): Birthdate of the citizen, default is "09 Feb 2001"
            occupation (str, optional): Occupation of the citizen, default is "Student"
            address (str, optional): Address of the citizen, default is "357/3 Namuang rd. 25000"

        Returns:
            Dict: info of the registration API
        """
        return {
            'citizen_id': citizen_id,
            'name': firstname,
            'surname': lastname,
            'birth_date': birthdate,
            'occupation': occupation,
            'address': address
        }

    def create_citizen_reservation_info(self,
                                        citizen_id="1103900076232",
                                        site_name="Chakkrapan",
                                        vaccine_name="Astra"):
        """Return new dict of the reservation API requested attributes.

        Args:
            citizen_id (str, optional): Identity Number of the reservation, default to be "1103900076232"
            site_name (str, optional): Site name of the reservation, default to be "Chakkrapan"
            vaccine_name (str, optional): Vaccine name of the reservation, default to be "Astrazeneca"

        Returns:
            Dict: info of the reservation API
        """

        return {
            'citizen_id': citizen_id,
            'site_name': site_name,
            'vaccine_name': vaccine_name
        }

    def received_feedback(self, response):
        """Return a feedback of the response

        Args:
            response (Response): response returned from a requested URL

        Returns:
            str: feedback
        """
        return response.json()['feedback']

    def test_reserve_a_citizen(self):
        """Test reserving a citizen with all valid attributes
        """
        # send request
        response_registration = requests.post(URL_registration, data=self.citizen_registration)
        response = requests.post(URL, data=self.citizen_reservation)
        # check the status code
        self.assertEqual(response.status_code, 200)  # 200 means ok!
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        self.assertEqual(self.received_feedback(response), FEEDBACK['success_reservation'])

    def test_reserve_with_missing_attribute(self):
        """Test reserving a citizen with some missing attribute
        """
        for info in self.missing_attribute:
            # send request
            response = requests.post(URL, data=info)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['missing_attribute'])

    def test_already_reserved(self):
        """Test reserving the same citizen twice
        """
        # send requests
        response_registration = requests.post(URL_registration, data=self.citizen_registration)
        response1 = requests.post(URL, data=self.citizen_reservation)
        response2 = requests.post(URL, data=self.citizen_reservation)
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        self.assertEqual(self.received_feedback(response1), FEEDBACK['success_reservation'])
        self.assertEqual(self.received_feedback(response2), FEEDBACK['reserved'])

    def test_reserve_without_registered(self):
        """Test reserving a citizen without registered
        """
        # send requests
        response = requests.post(URL, data=self.citizen_reservation)
        # check feedback
        self.assertEqual(self.received_feedback(response), FEEDBACK['not_registered'])

    def test_register_invalid_citizen_id(self):
        """Test register a person with invalid citizen_id
        """
        for info in self.invalid_citizen_id:
            # send request
            response = requests.post(URL, data=info)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['invalid_citizen_id'])

    def test_reserve_with_invalid_vaccine_name(self):
        """Test reserving a citizen with the invalid vaccine name
        """
        # send request
        response_registration = requests.post(URL_registration, data=self.citizen_registration)
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        for vaccine in self.invalid_vaccine_name:
            # send request
            response = requests.post(URL, data=vaccine)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['invalid_vaccine_name'])


if __name__ == '__main__':
    unittest.main()
