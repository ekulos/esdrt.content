def get_category_ldap_from_crf_code(value):
    """ get the CRF category this CRF Code matches
        According to the rules previously set
        for LDAP Matching
    """
    return CRF_CODES.get(value, {}).get('ldap', '')


def get_category_value_from_crf_code(value):
    """ get the CRF category value to show it in the observation metadata """

    # return CRF_CODES.get(value, {}).get('sectorname', '')
    return CRF_CODES.get(value, {}).get('title', '')


CRF_CODES = {
  "2C4": {
    "ldap": "sector6",
    "code": "2C4",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C4 Metal Industry - Magnesium Production"
  },
  "2C5": {
    "ldap": "sector6",
    "code": "2C5",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C5 Metal Industry - Lead Production"
  },
  "2C6": {
    "ldap": "sector6",
    "code": "2C6",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C6 Metal Industry - Zinc Production"
  },
  "2C1": {
    "ldap": "sector6",
    "code": "2C1",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C1 Metal Industry - Iron and Steel Production"
  },
  "2C2": {
    "ldap": "sector6",
    "code": "2C2",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C2 Metal Industry - Ferroalloys Production"
  },
  "2C3": {
    "ldap": "sector6",
    "code": "2C3",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2C3 Metal Industry - Aluminium Production"
  },
  "5E": {
    "ldap": "sector11",
    "code": "5E",
    "name": "5A-5F Waste",
    "title": "Other"
  },
  "5D": {
    "ldap": "sector11",
    "code": "5D",
    "name": "5A-5F Waste",
    "title": "Wastewater Treatment and Discharge"
  },
  "5F": {
    "ldap": "sector11",
    "code": "5F",
    "name": "5A-5F Waste",
    "title": "Memo Items"
  },
  "5A": {
    "ldap": "sector11",
    "code": "5A",
    "name": "5A-5F Waste",
    "title": "Solid Waste Disposal"
  },
  "5C": {
    "ldap": "sector11",
    "code": "5C",
    "name": "5A-5F Waste",
    "title": "Incineration and Open Burning of Waste"
  },
  "5B": {
    "ldap": "sector11",
    "code": "5B",
    "name": "5A-5F Waste",
    "title": "Biological Treatment of Solid Waste"
  },
  "1A1a": {
    "ldap": "sector1",
    "code": "1A1a",
    "name": "1A1 Energy industries",
    "title": "Public Electricity and Heat Production"
  },
  "1A1c": {
    "ldap": "sector1",
    "code": "1A1c",
    "name": "1A1 Energy industries",
    "title": "Manufacture of Solid Fuels and Other Energy Industries"
  },
  "1A1b": {
    "ldap": "sector1",
    "code": "1A1b",
    "name": "1A1 Energy industries",
    "title": "Petroleum Refining"
  },
  "4F1": {
    "ldap": "sector10",
    "code": "4F1",
    "name": "LULUCF",
    "title": "Other Land Remaining Other Land"
  },
  "4F2": {
    "ldap": "sector10",
    "code": "4F2",
    "name": "LULUCF",
    "title": "Land Converted to Other Land"
  },
  "2D": {
    "ldap": "sector6",
    "code": "2D",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "2D Non-Energy Products from Fuels and Solvent Use"
  },
  "2E": {
    "ldap": "sector7",
    "code": "2E",
    "name": "2E, 2F, 2G F-gases",
    "title": "2E Electronics Industry"
  },
  "2G": {
    "ldap": "sector7",
    "code": "2G",
    "name": "2E, 2F, 2G F-gases",
    "title": "2G Other Product Manufacture and Use"
  },
  "2H": {
    "ldap": "sector6",
    "code": "2H",
    "name": "2C, 2D, 2H Non-energy use of fuels, metal & electronics production",
    "title": "Other"
  },
  "1B2b": {
    "ldap": "sector4",
    "code": "1B2b",
    "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
    "title": "1B2b Fugitive Emissions from Fuels - Oil and Natural Gas and Other Emissions from Energy Production - Natural gas"
  },
  "1B2a": {
    "ldap": "sector4",
    "code": "1B2a",
    "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
    "title": "1B2a Fugitive Emissions from Fuels - Oil and Natural Gas and Other Emissions from Energy Production - Oil"
  },
  "3I": {
    "ldap": "sector9",
    "code": "3I",
    "name": "3C-3J Agriculture (soils)",
    "title": "Other Carbon-containing fertilizers"
  },
  "3H": {
    "ldap": "sector9",
    "code": "3H",
    "name": "3C-3J Agriculture (soils)",
    "title": "Urea application"
  },
  "3C": {
    "ldap": "sector9",
    "code": "3C",
    "name": "3C-3J Agriculture (soils)",
    "title": "Rice Cultivation"
  },
  "3B": {
    "ldap": "sector8",
    "code": "3B",
    "name": "3A, 3B Agriculture (animal production)",
    "title": "3B Manure Management"
  },
  "3A": {
    "ldap": "sector8",
    "code": "3A",
    "name": "3A, 3B Agriculture (animal production)",
    "title": "3A Enteric Fermentation"
  },
  "3G": {
    "ldap": "sector9",
    "code": "3G",
    "name": "3C-3J Agriculture (soils)",
    "title": "Liming"
  },
  "3F": {
    "ldap": "sector9",
    "code": "3F",
    "name": "3C-3J Agriculture (soils)",
    "title": "Fiend burning of agricultural residues"
  },
  "3E": {
    "ldap": "sector9",
    "code": "3E",
    "name": "3C-3J Agriculture (soils)",
    "title": "Prescribed burning of Savannas"
  },
  "7": {
    "ldap": "sector10",
    "code": "7",
    "name": "LULUCF",
    "title": "KP LULUCF"
  },
  "2F3": {
    "ldap": "sector7",
    "code": "2F3",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F3 Product Uses as Substitutes for Ozone Depleting Substances - Fire Protection"
  },
  "2F2": {
    "ldap": "sector7",
    "code": "2F2",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F2 Product Uses as Substitutes for Ozone Depleting Substances - Foam Blowing Agents"
  },
  "2F1": {
    "ldap": "sector7",
    "code": "2F1",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F1 Product Uses as Substitutes for Ozone Depleting Substances - Refrigeration and Air Conditioning"
  },
  "2F6": {
    "ldap": "sector7",
    "code": "2F6",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F6 Product Uses as Substitutes for Ozone Depleting Substances - Other Applications"
  },
  "2F5": {
    "ldap": "sector7",
    "code": "2F5",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F5 Product Uses as Substitutes for Ozone Depleting Substances - Solvents"
  },
  "2F4": {
    "ldap": "sector7",
    "code": "2F4",
    "name": "2E, 2F, 2G F-gases",
    "title": "2F4 Product Uses as Substitutes for Ozone Depleting Substances - Aerosolls"
  },
  "4A1": {
    "ldap": "sector10",
    "code": "4A1",
    "name": "LULUCF",
    "title": "Forest Land Remaining Forest Land"
  },
  "4A2": {
    "ldap": "sector10",
    "code": "4A2",
    "name": "LULUCF",
    "title": "Land Converted to Forest Land"
  },
  "2A4": {
    "ldap": "sector5",
    "code": "2A4",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2A4 Mineral Industry - Other Process Uses of Carbonates"
  },
  "2A2": {
    "ldap": "sector5",
    "code": "2A2",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2A2 Mineral Industry - Lime Production"
  },
  "2A3": {
    "ldap": "sector5",
    "code": "2A3",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2A3 Mineral Industry - Glass Production"
  },
  "2A1": {
    "ldap": "sector5",
    "code": "2A1",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2A1 Mineral industry - Cement Production"
  },
  "1D1a": {
    "ldap": "sector3",
    "code": "1D1a",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "International Bunkers - International Aviation"
  },
  "1D1b": {
    "ldap": "sector3",
    "code": "1D1b",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "International Bunkers - International Shipping"
  },
  "1C": {
    "ldap": "sector4",
    "code": "1C",
    "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
    "title": "1C Carbon Dioxide Transport and Storage"
  },
  "3D1": {
    "ldap": "sector9",
    "code": "3D1",
    "name": "3C-3J Agriculture (soils)",
    "title": "Direct N2O from managed soils"
  },
  "3D2": {
    "ldap": "sector9",
    "code": "3D2",
    "name": "3C-3J Agriculture (soils)",
    "title": "Indirect N2O from managed soils"
  },
  "4B1": {
    "ldap": "sector10",
    "code": "4B1",
    "name": "LULUCF",
    "title": "Cropland Remaining Cropland"
  },
  "4B2": {
    "ldap": "sector10",
    "code": "4B2",
    "name": "LULUCF",
    "title": "Land Converted to Cropland"
  },
  "1A5a": {
    "ldap": "sector2",
    "code": "1A5a",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Stationary"
  },
  "1A5b": {
    "ldap": "sector2",
    "code": "1A5b",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Mobile"
  },
  "1D4": {
    "ldap": "sector4",
    "code": "1D4",
    "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
    "title": "CO2 captured"
  },
  "1D2": {
    "ldap": "sector3",
    "code": "1D2",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "Multilateral Operations"
  },
  "1D1": {
    "ldap": "sector3",
    "code": "1D1",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "International Bunkers"
  },
  "1B1": {
    "ldap": "sector4",
    "code": "1B1",
    "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
    "title": "1B1 Fugitive emissions from fuels - Solid Fuels"
  },
  "6": {
    "ldap": "sector12",
    "code": "6",
    "name": "6 Other",
    "title": "Other"
  },
  "1A4b": {
    "ldap": "sector2",
    "code": "1A4b",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Residential"
  },
  "1A4c": {
    "ldap": "sector2",
    "code": "1A4c",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Agriculture/Forestry/Fishing"
  },
  "1A4a": {
    "ldap": "sector2",
    "code": "1A4a",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Commercial/Institutional"
  },
  "4C2": {
    "ldap": "sector10",
    "code": "4C2",
    "name": "LULUCF",
    "title": "Land Converted to Grassland"
  },
  "4C1": {
    "ldap": "sector10",
    "code": "4C1",
    "name": "LULUCF",
    "title": "Grassland Remaining Grassland"
  },
  "1A5": {
    "ldap": "sector2",
    "code": "1A5",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "1A5 Fuel Combustion Activities - Non- Specified"
  },
  "1A4": {
    "ldap": "sector2",
    "code": "1A4",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "1A4 Fuel Combustion Activities - Other Sectors"
  },
  "1A1": {
    "ldap": "sector1",
    "code": "1A1",
    "name": "1A1 Energy industries",
    "title": "1A1 Fuel Combustion Activities - Energy Industries"
  },
  "1A3": {
    "ldap": "sector3",
    "code": "1A3",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "Transport"
  },
  "1A2": {
    "ldap": "sector2",
    "code": "1A2",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "1A2 Fuel Combustion Activities - Manufacturing Industries and Construction"
  },
  "1A3c": {
    "ldap": "sector3",
    "code": "1A3c",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "1A3c Fuel Combustion Activities - Transport - Railways"
  },
  "1A3b": {
    "ldap": "sector3",
    "code": "1A3b",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "1A3b Fuel Combustion Activities - Transport - Road transportation"
  },
  "1A3a": {
    "ldap": "sector3",
    "code": "1A3a",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "1A3a Fuel Combustion Activities - Transport - Civil Aviation"
  },
  "1A3e": {
    "ldap": "sector3",
    "code": "1A3e",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "1A3e Fuel Combustion Activities - Transport - Other Transportation"
  },
  "1A3d": {
    "ldap": "sector3",
    "code": "1A3d",
    "name": "1A3 Transport, including international bunkers and 1D - memo items international aviation, shipping etc",
    "title": "1A3d Fuel Combustion Activities - Transport - Water-borne Navigation"
  },
  "4D2": {
    "ldap": "sector10",
    "code": "4D2",
    "name": "LULUCF",
    "title": "Land Converted to Wetlands"
  },
  "4D1": {
    "ldap": "sector10",
    "code": "4D1",
    "name": "LULUCF",
    "title": "Wetlands remaining wetlands"
  },
  "2B9": {
    "ldap": "sector5",
    "code": "2B9",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B9 Chemical Industry - Fluorochemical Production"
  },
  "2B8": {
    "ldap": "sector5",
    "code": "2B8",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B8 Chemical Industry - Petrochemical and Carbon Black Production"
  },
  "2B7": {
    "ldap": "sector5",
    "code": "2B7",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B7 Chemical Industry - Soda Ash Production"
  },
  "2B6": {
    "ldap": "sector5",
    "code": "2B6",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B6 Chemical industry - Titanium Dioxide Production"
  },
  "2B5": {
    "ldap": "sector5",
    "code": "2B5",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B5 Chemical industry - Carbide Production"
  },
  "2B4": {
    "ldap": "sector5",
    "code": "2B4",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B4 Chemical industry - Caprolactam"
  },
  "2B3": {
    "ldap": "sector5",
    "code": "2B3",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B3 Chemical industry - Adipic Acid Production"
  },
  "2B2": {
    "ldap": "sector5",
    "code": "2B2",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B2 Chemical industry - Nitric Acid Production"
  },
  "2B1": {
    "ldap": "sector5",
    "code": "2B1",
    "name": "2A, 2B Mineral and chemical industry",
    "title": "2B1 Chemical Industry - Ammonia Production"
  },
  "4H": {
    "ldap": "sector10",
    "code": "4H",
    "name": "LULUCF",
    "title": "Other"
  },
  "4G": {
    "ldap": "sector10",
    "code": "4G",
    "name": "LULUCF",
    "title": "Harvested Wood Products"
  },
  "1A2a": {
    "ldap": "sector2",
    "code": "1A2a",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Iron and Steel"
  },
  "1A2b": {
    "ldap": "sector2",
    "code": "1A2b",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Non-Ferrous Metals"
  },
  "1A2c": {
    "ldap": "sector2",
    "code": "1A2c",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Chemicals"
  },
  "1A2d": {
    "ldap": "sector2",
    "code": "1A2d",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Pulp, Paper and Print"
  },
  "1A2e": {
    "ldap": "sector2",
    "code": "1A2e",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Food Processing, Beverages and Tobacco"
  },
  "1A2f": {
    "ldap": "sector2",
    "code": "1A2f",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Non-Metallic Minerals"
  },
  "1A2g": {
    "ldap": "sector2",
    "code": "1A2g",
    "name": "1A2, 1A4, 1A5 Other energy sector",
    "title": "Other"
  },
  "1AB": {
    "ldap": "sector13",
    "code": "1AB",
    "name": "Reference approach Fuel combustion, reference approach",
    "title": "Reference Approach"
  },
  "4E1": {
    "ldap": "sector10",
    "code": "4E1",
    "name": "LULUCF",
    "title": "Settlements Remaining Settlements"
  },
  "4E2": {
    "ldap": "sector10",
    "code": "4E2",
    "name": "LULUCF",
    "title": "Land Converted to Settlements"
  }
}