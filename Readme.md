<h1>CSE543T housing price prediction</h1>

<h1> <a href="https://simplemaps.com/data/us-zips](https://docs.google.com/document/d/1ivS_cFVzJYx0SJhXoW5TKXcWKTyqRKazvDWh5FPlEyI/edit">Write up</a> </h1>

<h3>Install required packages</h3>
<p>
  Run <i>pip install -r requirements.txt</i> to install all the required package
</p>

<h3>Data acquisition</h3>
<ul>
  Data source:
  <li><a href="https://simplemaps.com/data/us-zips">US Zipcode</a></li>
  <li>
    <a
      href="https://www.ers.usda.gov/data-products/county-level-data-sets/download-data/"
      >Poverty & Unemployment & Median Household Income & Education</a
    >
  </li>
  <li>
    <a href="https://www.redfin.com/">Hosuing price & information: Redfin</a>
  </li>
  <li>Crime Rate, Minimum Wage: Kaggle</li>
</ul>

<h3>Acquire data</h3>
<ul>
  <li>
    <i>data_preparation1.py</i>: acquire link to properties from Redfin from
    zipcode, randomly partition the link to 10 parts, and save the link to
    houses in cvs files in folder<i>data/property_href</i>
  </li>
  <li>
    data_preparation2.py: acquire specific housing information from the links,
    and save the raw data in csv files in flies
    <i>data/housing_data_raw/{index}.csv</i>
  </li>
  <li>
    data_preparation3.py: Preprocess the raw data and combine them with crime
    rate, minimum wage, and poverty rate, etc to generate final data in
    <i>data/final_data.csv</i>
  </li>
</ul>

<h3>Ensemble model</h3>
<ul>
  <li>
    <i>ensemble_model/data.py</i>: Load the final data and generate the train
    and test set (80:20 ratio), the standardize the data
  </li>
  <li>
    <i>ensemble_model/cross_validation_sklearn.py</i>: Cross validate on models
    to find the best hyperparameters
  </li>
  <li>
    <i>ensemble_model/grid_search_output.txt</i>: output from running
    <i>cross_validation_sklearn.py</i>
  </li>
  <li>
    <i>ensemble_model/visualization.py</i>: visualize the result from
    <i>cross_validation_sklearn.py</i> and save the plots in
    <i>ensemble_model/plots</i>
  </li>
  <li>
    <i>ensemble_model/final_model.py</i>: Combine the models together and make
    prediction on test set
  </li>
</ul>
<h5>Accuracy achieved: 55.54%</h5>

<h3>Neural network: TODO - put st here when you guys are done</h3>
