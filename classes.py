class DailyRealData:
    def __init__(self, date, new_cases, cases_7_average, cases_14_average, total_cases):
        self.date = date
        self.new_cases = new_cases
        self.cases_7_average = cases_7_average
        self.cases_14_average = cases_14_average
        self.total_cases = total_cases
        
    def to_dict(self):
        return {
            "date": self.date,
            "newcases": self.new_cases,
            "cases_7_average": self.cases_7_average,
            "cases_14_average": self.cases_14_average,
            "total_cases": self.total_cases
        }