add allure zip file into project directory and add environment path to your system 
now generate allure report using

(venv)allure generate reports/allure-results --clean -o reports/allure-report

now serve rpor in default browser
allure serve reports/allure-results