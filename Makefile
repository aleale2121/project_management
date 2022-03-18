dev:
	docker-compose run app sh -c "python3 manage.py runserver"

makemg:
	   docker-compose run app sh -c "python3 manage.py makemigrations"

migrate:
   	   docker-compose run app sh -c "python3 manage.py migrate"


    