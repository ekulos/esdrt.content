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
    "1": {
        "ldap": "sector1",
        "code": "1",
        "name": "1A1 Energy industries",
        "title": "1 Energy"
    },
    "1A1": {
        "ldap": "sector1",
        "code": "1A1",
        "name": "1A1 Energy industries",
        "title": "1A1 Energy industries"
    },
    "1A1a": {
        "ldap": "sector1",
        "code": "1A1a",
        "name": "1A1 Energy industries",
        "title": "1A1a Public electricity and heat production"
    },
    "1A1b": {
        "ldap": "sector1",
        "code": "1A1b",
        "name": "1A1 Energy industries",
        "title": "1A1b Petroleum refining"
    },
    "1A1c": {
        "ldap": "sector1",
        "code": "1A1c",
        "name": "1A1 Energy industries",
        "title": "1A1c Manufacture of solid fuels and other energy industries"
    },
    "1A2": {
        "ldap": "sector2",
        "code": "1A2",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2 Manufacturing industries and construction"
    },
    "1A2a": {
        "ldap": "sector2",
        "code": "1A2a",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2a Iron and steel"
    },
    "1A2b": {
        "ldap": "sector2",
        "code": "1A2b",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2b Non-ferrous metals"
    },
    "1A2c": {
        "ldap": "sector2",
        "code": "1A2c",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2c Chemicals"
    },
    "1A2d": {
        "ldap": "sector2",
        "code": "1A2d",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2d Pulp, paper and print"
    },
    "1A2e": {
        "ldap": "sector2",
        "code": "1A2e",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2e Food processing, beverages and tobacco"
    },
    "1A2f": {
        "ldap": "sector2",
        "code": "1A2f",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2f Non-metallic minerals"
    },
    "1A2g": {
        "ldap": "sector2",
        "code": "1A2g",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A2g Other (manufacturing industries and construction)"
    },
    "1A4": {
        "ldap": "sector2",
        "code": "1A4",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A4 Other sectors (fuel combustion activities)"
    },
    "1A4a": {
        "ldap": "sector2",
        "code": "1A4a",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A4a Commercial/institutional"
    },
    "1A4b": {
        "ldap": "sector2",
        "code": "1A4b",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A4b Residential"
    },
    "1A4c": {
        "ldap": "sector2",
        "code": "1A4c",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A4c Agriculture/forestry/fishing"
    },
    "1A5": {
        "ldap": "sector2",
        "code": "1A5",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A5 Other (fuel combustion activities)"
    },
    "1A5a": {
        "ldap": "sector2",
        "code": "1A5a",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A5a Stationary"
    },
    "1A5b": {
        "ldap": "sector2",
        "code": "1A5b",
        "name": "1A2, 1A4, 1A5 Other energy sector",
        "title": "1A5b Mobile"
    },
    "1A3": {
        "ldap": "sector3",
        "code": "1A3",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3 Transport"
    },
    "1A3a": {
        "ldap": "sector3",
        "code": "1A3a",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3a Domestic aviation"
    },
    "1A3b": {
        "ldap": "sector3",
        "code": "1A3b",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3b Road transportation"
    },
    "1A3c": {
        "ldap": "sector3",
        "code": "1A3c",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3c Railways"
    },
    "1A3d": {
        "ldap": "sector3",
        "code": "1A3d",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3d Domestic navigation"
    },
    "1A3e": {
        "ldap": "sector3",
        "code": "1A3e",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1A3e Other transportation"
    },
    "1D": {
        "ldap": "sector3",
        "code": "1D",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D Memo items (energy)"
    },
    "1D1": {
        "ldap": "sector3",
        "code": "1D1",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D1 International bunkers"
    },
    "1D1a": {
        "ldap": "sector3",
        "code": "1D1a",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D1a Aviation (international bunkers)"
    },
    "1D1b": {
        "ldap": "sector3",
        "code": "1D1b",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D1b Navigation (international bunkers)"
    },
    "1D2": {
        "ldap": "sector3",
        "code": "1D2",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D2 Multilateral operations"
    },
    "1D3": {
        "ldap": "sector3",
        "code": "1D3",
        "name": "1A3, 1D Transport and memo items (energy)",
        "title": "1D3 CO2 emissions from biomass"
    },
    "1B": {
        "ldap": "sector4",
        "code": "1B",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B Fugitive emissions from fuels"
    },
    "1B1": {
        "ldap": "sector4",
        "code": "1B1",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B1 Fugitive emissions from solid fuels"
    },
    "1B2": {
        "ldap": "sector4",
        "code": "1B2",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B2 Fugitive emissions from oil and natural gas and other emissions"
    },
    "1B2a": {
        "ldap": "sector4",
        "code": "1B2a",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B2a Fugitive emissions from oil"
    },
    "1B2b": {
        "ldap": "sector4",
        "code": "1B2b",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B2b Fugitive emissions from natural gas"
    },
    "1B2c": {
        "ldap": "sector4",
        "code": "1B2c",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1B2c Fugitive emissions from venting/flaring"
    },
    "1C": {
        "ldap": "sector4",
        "code": "1C",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1C CO2 transport and storage"
    },
    "1D4": {
        "ldap": "sector4",
        "code": "1D4",
        "name": "1B, 1C Fugitive emissions, CO2 transport and storage",
        "title": "1D4 CO2 captured"
    },
    "2": {
        "ldap": "sector5",
        "code": "2",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2 Industrial processes and product use"
    },
    "2A": {
        "ldap": "sector5",
        "code": "2A",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2A Mineral industry"
    },
    "2A1": {
        "ldap": "sector5",
        "code": "2A1",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2A1 Cement production"
    },
    "2A2": {
        "ldap": "sector5",
        "code": "2A2",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2A2 Lime production"
    },
    "2A3": {
        "ldap": "sector5",
        "code": "2A3",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2A3 Glass production"
    },
    "2A4": {
        "ldap": "sector5",
        "code": "2A4",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2A4 Other process uses of carbonates"
    },
    "2B": {
        "ldap": "sector5",
        "code": "2B",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B Chemical industry"
    },
    "2B1": {
        "ldap": "sector5",
        "code": "2B1",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B1 Ammonia production"
    },
    "2B2": {
        "ldap": "sector5",
        "code": "2B2",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B2 Nitric acid production"
    },
    "2B3": {
        "ldap": "sector5",
        "code": "2B3",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B3 Adipic acid production"
    },
    "2B4": {
        "ldap": "sector5",
        "code": "2B4",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B4 Caprolactam, glyoxal and glyoxylic acid production"
    },
    "2B5": {
        "ldap": "sector5",
        "code": "2B5",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B5 Carbide production"
    },
    "2B6": {
        "ldap": "sector5",
        "code": "2B6",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B6 Titanium dioxide production"
    },
    "2B7": {
        "ldap": "sector5",
        "code": "2B7",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B7 Soda ash production"
    },
    "2B8": {
        "ldap": "sector5",
        "code": "2B8",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B8 Petrochemical and carbon black production"
    },
    "2B9": {
        "ldap": "sector5",
        "code": "2B9",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B9 Fluorochemical production"
    },
    "2B10": {
        "ldap": "sector5",
        "code": "2B10",
        "name": "2A, 2B Mineral and chemical industries",
        "title": "2B10 Other (chemical industry)"
    },
    "2C": {
        "ldap": "sector6",
        "code": "2C",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C Metal industry"
    },
    "2C1": {
        "ldap": "sector6",
        "code": "2C1",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C1 Iron and steel production"
    },
    "2C2": {
        "ldap": "sector6",
        "code": "2C2",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C2 Ferroalloys production"
    },
    "2C3": {
        "ldap": "sector6",
        "code": "2C3",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C3 Aluminium production"
    },
    "2C4": {
        "ldap": "sector6",
        "code": "2C4",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C4 Magnesium production"
    },
    "2C5": {
        "ldap": "sector6",
        "code": "2C5",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C5 Lead production"
    },
    "2C6": {
        "ldap": "sector6",
        "code": "2C6",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C6 Zinc production"
    },
    "2C7": {
        "ldap": "sector6",
        "code": "2C7",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2C7 Other (metal industry)"
    },
    "2D": {
        "ldap": "sector6",
        "code": "2D",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2D Non-energy products from fuels and solvent use"
    },
    "2H": {
        "ldap": "sector6",
        "code": "2H",
        "name": "2C, 2D, 2H Metal industry, non-energy products from fuels, solvent use and other industrial processes",
        "title": "2H Other (industrial processes)"
    },
    "2E": {
        "ldap": "sector7",
        "code": "2E",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2E Electronics industry"
    },
    "2F": {
        "ldap": "sector7",
        "code": "2F",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F Product uses as substitutes for ozone depleting substances"
    },
    "2F1": {
        "ldap": "sector7",
        "code": "2F1",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F1 Refrigeration and air conditioning"
    },
    "2F2": {
        "ldap": "sector7",
        "code": "2F2",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F2 Foam blowing agents"
    },
    "2F3": {
        "ldap": "sector7",
        "code": "2F3",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F3 Fire protection"
    },
    "2F4": {
        "ldap": "sector7",
        "code": "2F4",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F4 Aerosols"
    },
    "2F5": {
        "ldap": "sector7",
        "code": "2F5",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F5 Solvents"
    },
    "2F6": {
        "ldap": "sector7",
        "code": "2F6",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2F6 Other applications (product uses as substitutes for ODS)"
    },
    "2G": {
        "ldap": "sector7",
        "code": "2G",
        "name": "2E, 2F, 2G Electronics industry, product uses as ODS substitutes, and other products manufacture and use",
        "title": "2G Other product manufacture and use"
    },
    "3": {
        "ldap": "sector8",
        "code": "3",
        "name": "3A, 3B Agriculture (livestock)",
        "title": "3 Agriculture"
    },
    "3A": {
        "ldap": "sector8",
        "code": "3A",
        "name": "3A, 3B Agriculture (livestock)",
        "title": "3A Enteric fermentation"
    },
    "3B": {
        "ldap": "sector8",
        "code": "3B",
        "name": "3A, 3B Agriculture (livestock)",
        "title": "3B Manure management"
    },
    "3C": {
        "ldap": "sector9",
        "code": "3C",
        "name": "3C-3J Agriculture (land)",
        "title": "3C Rice cultivation"
    },
    "3D": {
        "ldap": "sector9",
        "code": "3D",
        "name": "3C-3J Agriculture (land)",
        "title": "3D Agricultural soils"
    },
    "3D1": {
        "ldap": "sector9",
        "code": "3D1",
        "name": "3C-3J Agriculture (land)",
        "title": "3D1 Direct N2O emissions from managed soils"
    },
    "3D2": {
        "ldap": "sector9",
        "code": "3D2",
        "name": "3C-3J Agriculture (land)",
        "title": "3D2 Indirect N2O emissions from managed soils"
    },
    "3E": {
        "ldap": "sector9",
        "code": "3E",
        "name": "3C-3J Agriculture (land)",
        "title": "3E Prescribed burning of savannas"
    },
    "3F": {
        "ldap": "sector9",
        "code": "3F",
        "name": "3C-3J Agriculture (land)",
        "title": "3F Field burning of agricultural residues"
    },
    "3G": {
        "ldap": "sector9",
        "code": "3G",
        "name": "3C-3J Agriculture (land)",
        "title": "3G Liming"
    },
    "3H": {
        "ldap": "sector9",
        "code": "3H",
        "name": "3C-3J Agriculture (land)",
        "title": "3H Urea application"
    },
    "3I": {
        "ldap": "sector9",
        "code": "3I",
        "name": "3C-3J Agriculture (land)",
        "title": "3I Other carbon-containing fertilizers"
    },
    "3J": {
        "ldap": "sector9",
        "code": "3J",
        "name": "3C-3J Agriculture (land)",
        "title": "3J Other (agriculture)"
    },
    "4": {
        "ldap": "sector10",
        "code": "4",
        "name": "4, 7 LULUCF",
        "title": "4 Land use, land-use change and forestry"
    },
    "4A": {
        "ldap": "sector10",
        "code": "4A",
        "name": "4, 7 LULUCF",
        "title": "4A Forest land"
    },
    "4A1": {
        "ldap": "sector10",
        "code": "4A1",
        "name": "4, 7 LULUCF",
        "title": "4A1 Forest land remaining forest land"
    },
    "4A2": {
        "ldap": "sector10",
        "code": "4A2",
        "name": "4, 7 LULUCF",
        "title": "4A2 Land converted to forest land"
    },
    "4B": {
        "ldap": "sector10",
        "code": "4B",
        "name": "4, 7 LULUCF",
        "title": "4B Cropland"
    },
    "4B1": {
        "ldap": "sector10",
        "code": "4B1",
        "name": "4, 7 LULUCF",
        "title": "4B1 Cropland remaining cropland"
    },
    "4B2": {
        "ldap": "sector10",
        "code": "4B2",
        "name": "4, 7 LULUCF",
        "title": "4B2 Land converted to cropland"
    },
    "4C": {
        "ldap": "sector10",
        "code": "4C",
        "name": "4, 7 LULUCF",
        "title": "4C Grassland"
    },
    "4C1": {
        "ldap": "sector10",
        "code": "4C1",
        "name": "4, 7 LULUCF",
        "title": "4C1 Grassland remaining grassland"
    },
    "4C2": {
        "ldap": "sector10",
        "code": "4C2",
        "name": "4, 7 LULUCF",
        "title": "4C2 Land converted to grassland"
    },
    "4D": {
        "ldap": "sector10",
        "code": "4D",
        "name": "4, 7 LULUCF",
        "title": "4D Wetlands"
    },
    "4D1": {
        "ldap": "sector10",
        "code": "4D1",
        "name": "4, 7 LULUCF",
        "title": "4D1 Wetlands remaining wetlands"
    },
    "4D2": {
        "ldap": "sector10",
        "code": "4D2",
        "name": "4, 7 LULUCF",
        "title": "4D2 Land converted to wetlands"
    },
    "4E": {
        "ldap": "sector10",
        "code": "4E",
        "name": "4, 7 LULUCF",
        "title": "4E Settlements"
    },
    "4E1": {
        "ldap": "sector10",
        "code": "4E1",
        "name": "4, 7 LULUCF",
        "title": "4E1 Settlements remaining settlements"
    },
    "4E2": {
        "ldap": "sector10",
        "code": "4E2",
        "name": "4, 7 LULUCF",
        "title": "4E2 Land converted to settlements"
    },
    "4F": {
        "ldap": "sector10",
        "code": "4F",
        "name": "4, 7 LULUCF",
        "title": "4F Other land"
    },
    "4F1": {
        "ldap": "sector10",
        "code": "4F1",
        "name": "4, 7 LULUCF",
        "title": "4F1 Other land remaining other land"
    },
    "4F2": {
        "ldap": "sector10",
        "code": "4F2",
        "name": "4, 7 LULUCF",
        "title": "4F2 Land converted to other land"
    },
    "4G": {
        "ldap": "sector10",
        "code": "4G",
        "name": "4, 7 LULUCF",
        "title": "4G Harvested wood products"
    },
    "4H": {
        "ldap": "sector10",
        "code": "4H",
        "name": "4, 7 LULUCF",
        "title": "4H Other (LULUCF)"
    },
    "7": {
        "ldap": "sector10",
        "code": "7",
        "name": "4, 7 LULUCF",
        "title": "7 KP LULUCF"
    },
    "5": {
        "ldap": "sector11",
        "code": "5",
        "name": "5 Waste",
        "title": "5 Waste"
    },
    "5A": {
        "ldap": "sector11",
        "code": "5A",
        "name": "5 Waste",
        "title": "5A Solid waste disposal"
    },
    "5B": {
        "ldap": "sector11",
        "code": "5B",
        "name": "5 Waste",
        "title": "5B Biological treatment of solid waste"
    },
    "5C": {
        "ldap": "sector11",
        "code": "5C",
        "name": "5 Waste",
        "title": "5C Incineration and open burning of waste"
    },
    "5D": {
        "ldap": "sector11",
        "code": "5D",
        "name": "5 Waste",
        "title": "5D Wastewater treatment and discharge"
    },
    "5E": {
        "ldap": "sector11",
        "code": "5E",
        "name": "5 Waste",
        "title": "5E Other (waste)"
    },
    "5F": {
        "ldap": "sector11",
        "code": "5F",
        "name": "5 Waste",
        "title": "5F Memo items (waste)"
    },
    "0": {
        "ldap": "sector12",
        "code": "0",
        "name": "0, 6 Cross cutting and other",
        "title": "0 Cross cutting"
    },
    "6": {
        "ldap": "sector12",
        "code": "6",
        "name": "0, 6 Cross cutting and other",
        "title": "6 Other (greenhouse gas source and sink categories)"
    },
    "1AB": {
        "ldap": "sector13",
        "code": "1AB",
        "name": "1AB Reference approach",
        "title": "1AB Reference approach"
    }
}
