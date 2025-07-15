/**
 * Location Service for Address Suggestions and Geocoding
 * Provides location suggestions for booking forms
 */

class LocationService {
  constructor() {
    this.cache = new Map();
    this.currentLocationCache = null;
    this.currentLocationTimestamp = null;
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Comprehensive Indian locations database with detailed state-wise data
   */
  getPopularLocations() {
    return {
      // ODISHA STATE - Complete Database
      odisha: {
        tier1_cities: [
          { name: "Bhubaneswar", address: "Bhubaneswar, Odisha", type: "city", lat: 20.2961, lng: 85.8245, population: "837,737" },
          { name: "Cuttack", address: "Cuttack, Odisha", type: "city", lat: 20.4625, lng: 85.8828, population: "606,007" }
        ],
        tier2_cities: [
          { name: "Rourkela", address: "Rourkela, Sundargarh, Odisha", type: "city", lat: 22.2604, lng: 84.8536, population: "483,640" },
          { name: "Brahmapur", address: "Brahmapur, Ganjam, Odisha", type: "city", lat: 19.3149, lng: 84.7941, population: "355,823" },
          { name: "Sambalpur", address: "Sambalpur, Odisha", type: "city", lat: 21.4669, lng: 83.9812, population: "335,761" },
          { name: "Puri", address: "Puri, Odisha", type: "city", lat: 19.8135, lng: 85.8312, population: "200,564" },
          { name: "Balasore", address: "Balasore, Odisha", type: "city", lat: 21.4942, lng: 86.9336, population: "188,811" },
          { name: "Baripada", address: "Baripada, Mayurbhanj, Odisha", type: "city", lat: 21.9347, lng: 86.7350, population: "116,693" }
        ],
        tier3_towns: [
          { name: "Jharsuguda", address: "Jharsuguda, Odisha", type: "town", lat: 21.8556, lng: 84.0086, population: "67,675" },
          { name: "Jeypore", address: "Jeypore, Koraput, Odisha", type: "town", lat: 18.8557, lng: 82.5678, population: "75,823" },
          { name: "Barbil", address: "Barbil, Keonjhar, Odisha", type: "town", lat: 22.1167, lng: 85.3833, population: "64,835" },
          { name: "Khordha", address: "Khordha, Odisha", type: "town", lat: 20.1821, lng: 85.6186, population: "59,173" },
          { name: "Silchar", address: "Silchar, Cachar, Odisha", type: "town", lat: 19.8207, lng: 85.8355, population: "55,234" },
          { name: "Rayagada", address: "Rayagada, Odisha", type: "town", lat: 19.1664, lng: 83.4126, population: "67,852" },
          { name: "Kendrapara", address: "Kendrapara, Odisha", type: "town", lat: 20.5007, lng: 86.4219, population: "52,905" },
          { name: "Dhenkanal", address: "Dhenkanal, Odisha", type: "town", lat: 20.6593, lng: 85.5955, population: "67,822" },
          { name: "Koraput", address: "Koraput, Odisha", type: "town", lat: 18.8120, lng: 82.7060, population: "45,823" },
          { name: "Bolangir", address: "Bolangir, Odisha", type: "town", lat: 20.7167, lng: 83.4500, population: "61,143" }
        ],
        villages: [
          { name: "Konark", address: "Konark, Puri, Odisha", type: "village", lat: 19.8876, lng: 86.0945, famous_for: "Sun Temple" },
          { name: "Chilika", address: "Chilika, Khordha, Odisha", type: "village", lat: 19.7167, lng: 85.3167, famous_for: "Chilika Lake" },
          { name: "Gopalpur", address: "Gopalpur, Ganjam, Odisha", type: "village", lat: 19.2667, lng: 84.9167, famous_for: "Beach Resort" },
          { name: "Chandipur", address: "Chandipur, Balasore, Odisha", type: "village", lat: 21.4500, lng: 87.0333, famous_for: "Vanishing Sea Beach" },
          { name: "Simlipal", address: "Simlipal, Mayurbhanj, Odisha", type: "village", lat: 21.6667, lng: 86.5000, famous_for: "National Park" },
          { name: "Bhitarkanika", address: "Bhitarkanika, Kendrapara, Odisha", type: "village", lat: 20.6833, lng: 86.9000, famous_for: "Mangrove Sanctuary" },
          { name: "Daringbadi", address: "Daringbadi, Kandhamal, Odisha", type: "village", lat: 19.9167, lng: 84.1667, famous_for: "Kashmir of Odisha" },
          { name: "Taptapani", address: "Taptapani, Ganjam, Odisha", type: "village", lat: 19.4000, lng: 84.4000, famous_for: "Hot Springs" },
          { name: "Satkosia", address: "Satkosia, Angul, Odisha", type: "village", lat: 20.5333, lng: 84.6667, famous_for: "Tiger Reserve" },
          { name: "Hirakud", address: "Hirakud, Sambalpur, Odisha", type: "village", lat: 21.5333, lng: 83.8667, famous_for: "Hirakud Dam" }
        ],
        airports: [
          { name: "Biju Patnaik International Airport", address: "Bhubaneswar Airport, Odisha", type: "airport", lat: 20.2444, lng: 85.8178, code: "BBI" },
          { name: "Jharsuguda Airport", address: "Veer Surendra Sai Airport, Jharsuguda, Odisha", type: "airport", lat: 21.9133, lng: 84.0506, code: "JRG" }
        ],
        transport: [
          { name: "Bhubaneswar Railway Station", address: "Bhubaneswar Railway Station, Odisha", type: "transport", lat: 20.2700, lng: 85.8400 },
          { name: "Cuttack Railway Station", address: "Cuttack Railway Station, Odisha", type: "transport", lat: 20.4625, lng: 85.8828 },
          { name: "Puri Railway Station", address: "Puri Railway Station, Odisha", type: "transport", lat: 19.8135, lng: 85.8312 },
          { name: "Sambalpur Railway Station", address: "Sambalpur Railway Station, Odisha", type: "transport", lat: 21.4669, lng: 83.9812 }
        ],
        government: [
          { name: "Odisha Secretariat", address: "Lok Seva Bhawan, Bhubaneswar, Odisha", type: "government", lat: 20.2700, lng: 85.8400 },
          { name: "Odisha High Court", address: "High Court of Orissa, Cuttack, Odisha", type: "government", lat: 20.4625, lng: 85.8828 },
          { name: "Raj Bhawan Odisha", address: "Raj Bhawan, Bhubaneswar, Odisha", type: "government", lat: 20.2700, lng: 85.8400 }
        ]
      },

      // ANDHRA PRADESH STATE - Complete Database
      andhra_pradesh: {
        tier1_cities: [
          { name: "Visakhapatnam", address: "Visakhapatnam, Andhra Pradesh", type: "city", lat: 17.6868, lng: 83.2185, population: "2,035,922" },
          { name: "Vijayawada", address: "Vijayawada, Krishna, Andhra Pradesh", type: "city", lat: 16.5062, lng: 80.6480, population: "1,048,240" },
          { name: "Guntur", address: "Guntur, Andhra Pradesh", type: "city", lat: 16.3067, lng: 80.4365, population: "743,354" },
          { name: "Nellore", address: "Nellore, Andhra Pradesh", type: "city", lat: 14.4426, lng: 79.9865, population: "505,258" },
          { name: "Kurnool", address: "Kurnool, Andhra Pradesh", type: "city", lat: 15.8281, lng: 78.0373, population: "484,327" }
        ],
        tier2_cities: [
          { name: "Rajahmundry", address: "Rajahmundry, East Godavari, Andhra Pradesh", type: "city", lat: 17.0005, lng: 81.8040, population: "341,831" },
          { name: "Tirupati", address: "Tirupati, Chittoor, Andhra Pradesh", type: "city", lat: 13.6288, lng: 79.4192, population: "287,035" },
          { name: "Anantapur", address: "Anantapur, Andhra Pradesh", type: "city", lat: 14.6819, lng: 77.6006, population: "267,161" },
          { name: "Eluru", address: "Eluru, West Godavari, Andhra Pradesh", type: "city", lat: 16.7107, lng: 81.0953, population: "214,414" },
          { name: "Ongole", address: "Ongole, Prakasam, Andhra Pradesh", type: "city", lat: 15.5057, lng: 80.0499, population: "186,292" },
          { name: "Chittoor", address: "Chittoor, Andhra Pradesh", type: "city", lat: 13.2172, lng: 79.1003, population: "153,756" },
          { name: "Machilipatnam", address: "Machilipatnam, Krishna, Andhra Pradesh", type: "city", lat: 16.1875, lng: 81.1389, population: "183,370" }
        ],
        tier3_towns: [
          { name: "Kadapa", address: "Kadapa, Andhra Pradesh", type: "town", lat: 14.4673, lng: 78.8242, population: "344,893" },
          { name: "Vizianagaram", address: "Vizianagaram, Andhra Pradesh", type: "town", lat: 18.1167, lng: 83.4000, population: "228,025" },
          { name: "Adoni", address: "Adoni, Kurnool, Andhra Pradesh", type: "town", lat: 15.6281, lng: 77.2750, population: "166,344" },
          { name: "Tenali", address: "Tenali, Guntur, Andhra Pradesh", type: "town", lat: 16.2333, lng: 80.6500, population: "164,937" },
          { name: "Proddatur", address: "Proddatur, Kadapa, Andhra Pradesh", type: "town", lat: 14.7500, lng: 78.5500, population: "164,776" },
          { name: "Hindupur", address: "Hindupur, Anantapur, Andhra Pradesh", type: "town", lat: 13.8281, lng: 77.4911, population: "151,677" },
          { name: "Bhimavaram", address: "Bhimavaram, West Godavari, Andhra Pradesh", type: "town", lat: 16.5449, lng: 81.5212, population: "142,184" },
          { name: "Madanapalle", address: "Madanapalle, Chittoor, Andhra Pradesh", type: "town", lat: 13.5500, lng: 78.5000, population: "107,512" },
          { name: "Guntakal", address: "Guntakal, Anantapur, Andhra Pradesh", type: "town", lat: 15.1667, lng: 77.3667, population: "126,270" },
          { name: "Dharmavaram", address: "Dharmavaram, Anantapur, Andhra Pradesh", type: "town", lat: 14.4167, lng: 77.7167, population: "107,512" }
        ],
        villages: [
          { name: "Lepakshi", address: "Lepakshi, Anantapur, Andhra Pradesh", type: "village", lat: 14.1167, lng: 77.6167, famous_for: "Veerabhadra Temple" },
          { name: "Srikalahasti", address: "Srikalahasti, Chittoor, Andhra Pradesh", type: "village", lat: 13.7500, lng: 79.7000, famous_for: "Kalahasti Temple" },
          { name: "Amaravati", address: "Amaravati, Guntur, Andhra Pradesh", type: "village", lat: 16.5742, lng: 80.3568, famous_for: "New Capital City" },
          { name: "Hampi", address: "Hampi, Ballari, Andhra Pradesh", type: "village", lat: 15.3350, lng: 76.4600, famous_for: "UNESCO World Heritage Site" },
          { name: "Araku Valley", address: "Araku Valley, Visakhapatnam, Andhra Pradesh", type: "village", lat: 18.3273, lng: 82.8779, famous_for: "Hill Station" },
          { name: "Horsley Hills", address: "Horsley Hills, Chittoor, Andhra Pradesh", type: "village", lat: 13.6667, lng: 78.4000, famous_for: "Hill Station" },
          { name: "Borra Caves", address: "Borra Caves, Visakhapatnam, Andhra Pradesh", type: "village", lat: 18.2833, lng: 83.0333, famous_for: "Limestone Caves" },
          { name: "Gandikota", address: "Gandikota, Kadapa, Andhra Pradesh", type: "village", lat: 14.6833, lng: 78.2667, famous_for: "Grand Canyon of India" },
          { name: "Belum Caves", address: "Belum Caves, Kurnool, Andhra Pradesh", type: "village", lat: 15.1167, lng: 78.0500, famous_for: "Underground Caves" },
          { name: "Nagarjuna Sagar", address: "Nagarjuna Sagar, Nalgonda, Andhra Pradesh", type: "village", lat: 16.5667, lng: 79.3000, famous_for: "Dam & Buddhist Site" }
        ],
        airports: [
          { name: "Visakhapatnam Airport", address: "Visakhapatnam Airport, Andhra Pradesh", type: "airport", lat: 17.7211, lng: 83.2245, code: "VTZ" },
          { name: "Vijayawada Airport", address: "Gannavaram Airport, Vijayawada, Andhra Pradesh", type: "airport", lat: 16.5304, lng: 80.7968, code: "VGA" },
          { name: "Tirupati Airport", address: "Tirupati Airport, Andhra Pradesh", type: "airport", lat: 13.6325, lng: 79.5433, code: "TIR" },
          { name: "Kadapa Airport", address: "Cuddapah Airport, Kadapa, Andhra Pradesh", type: "airport", lat: 14.5109, lng: 78.7739, code: "CDP" }
        ]
      },

      // KARNATAKA STATE (Enhanced)
      karnataka: {
        tier1_cities: [
          { name: "Bangalore", address: "Bangalore, Karnataka", type: "city", lat: 12.9716, lng: 77.5946, population: "8,443,675" },
          { name: "Mysore", address: "Mysore, Karnataka", type: "city", lat: 12.2958, lng: 76.6394, population: "920,550" },
          { name: "Hubli-Dharwad", address: "Hubli-Dharwad, Karnataka", type: "city", lat: 15.3647, lng: 75.1240, population: "943,857" }
        ],
        bangalore_areas: [
          { name: "HAL Headquarters", address: "HAL Airport Road, Bangalore, Karnataka", type: "office", lat: 12.9716, lng: 77.5946 },
          { name: "Electronic City", address: "Electronic City, Bangalore, Karnataka", type: "tech_hub", lat: 12.8456, lng: 77.6603 },
          { name: "Whitefield", address: "Whitefield, Bangalore, Karnataka", type: "tech_hub", lat: 12.9698, lng: 77.7500 },
          { name: "Koramangala", address: "Koramangala, Bangalore, Karnataka", type: "commercial", lat: 12.9279, lng: 77.6271 },
          { name: "Indiranagar", address: "Indiranagar, Bangalore, Karnataka", type: "commercial", lat: 12.9784, lng: 77.6408 },
          { name: "MG Road", address: "MG Road, Bangalore, Karnataka", type: "commercial", lat: 12.9759, lng: 77.6037 },
          { name: "Silk Board", address: "Silk Board Junction, Bangalore, Karnataka", type: "transport", lat: 12.9165, lng: 77.6224 },
          { name: "Marathahalli", address: "Marathahalli, Bangalore, Karnataka", type: "commercial", lat: 12.9591, lng: 77.6974 },
          { name: "Hebbal", address: "Hebbal, Bangalore, Karnataka", type: "transport", lat: 13.0358, lng: 77.5970 },
          { name: "Banashankari", address: "Banashankari, Bangalore, Karnataka", type: "residential", lat: 12.9250, lng: 77.5667 },
          { name: "Kempegowda International Airport", address: "KIAL, Bangalore, Karnataka", type: "airport", lat: 13.1986, lng: 77.7066 },
          { name: "Bangalore City Railway Station", address: "KSR Railway Station, Bangalore, Karnataka", type: "transport", lat: 12.9767, lng: 77.5993 }
        ]
      },

      // TELANGANA STATE - Complete Database
      telangana: {
        tier1_cities: [
          { name: "Hyderabad", address: "Hyderabad, Telangana", type: "city", lat: 17.3850, lng: 78.4867, population: "6,809,970" },
          { name: "Secunderabad", address: "Secunderabad, Telangana", type: "city", lat: 17.4399, lng: 78.4983, population: "204,182" }
        ],
        tier2_cities: [
          { name: "Warangal", address: "Warangal, Telangana", type: "city", lat: 17.9689, lng: 79.5941, population: "704,570" },
          { name: "Nizamabad", address: "Nizamabad, Telangana", type: "city", lat: 18.6725, lng: 78.0941, population: "311,152" },
          { name: "Khammam", address: "Khammam, Telangana", type: "city", lat: 17.2473, lng: 80.1514, population: "262,255" },
          { name: "Karimnagar", address: "Karimnagar, Telangana", type: "city", lat: 18.4386, lng: 79.1288, population: "297,447" },
          { name: "Ramagundam", address: "Ramagundam, Peddapalli, Telangana", type: "city", lat: 18.7581, lng: 79.4738, population: "229,644" },
          { name: "Mahbubnagar", address: "Mahbubnagar, Telangana", type: "city", lat: 16.7302, lng: 77.9982, population: "147,747" }
        ],
        tier3_towns: [
          { name: "Adilabad", address: "Adilabad, Telangana", type: "town", lat: 19.6669, lng: 78.5311, population: "108,233" },
          { name: "Suryapet", address: "Suryapet, Telangana", type: "town", lat: 17.1400, lng: 79.6200, population: "102,395" },
          { name: "Miryalaguda", address: "Miryalaguda, Nalgonda, Telangana", type: "town", lat: 16.8667, lng: 79.5667, population: "95,676" },
          { name: "Jagtial", address: "Jagtial, Telangana", type: "town", lat: 18.7900, lng: 78.9100, population: "73,123" },
          { name: "Mancherial", address: "Mancherial, Telangana", type: "town", lat: 18.8700, lng: 79.4600, population: "71,639" },
          { name: "Nalgonda", address: "Nalgonda, Telangana", type: "town", lat: 17.0500, lng: 79.2700, population: "135,744" },
          { name: "Siddipet", address: "Siddipet, Telangana", type: "town", lat: 18.1018, lng: 78.8548, population: "63,225" },
          { name: "Bodhan", address: "Bodhan, Nizamabad, Telangana", type: "town", lat: 18.6667, lng: 77.9000, population: "52,704" },
          { name: "Sangareddy", address: "Sangareddy, Telangana", type: "town", lat: 17.6167, lng: 78.0833, population: "61,520" },
          { name: "Medak", address: "Medak, Telangana", type: "town", lat: 18.0500, lng: 78.2700, population: "50,623" }
        ],
        villages: [
          { name: "Ramoji Film City", address: "Ramoji Film City, Hyderabad, Telangana", type: "village", lat: 17.2544, lng: 78.6808, famous_for: "World's Largest Film Studio" },
          { name: "Yadagirigutta", address: "Yadagirigutta, Yadadri, Telangana", type: "village", lat: 17.5833, lng: 78.9000, famous_for: "Lakshmi Narasimha Temple" },
          { name: "Bhadrachalam", address: "Bhadrachalam, Kothagudem, Telangana", type: "village", lat: 17.6667, lng: 80.8833, famous_for: "Rama Temple" },
          { name: "Alampur", address: "Alampur, Jogulamba Gadwal, Telangana", type: "village", lat: 15.8833, lng: 78.1333, famous_for: "Navabrahma Temples" },
          { name: "Kaleshwaram", address: "Kaleshwaram, Jayashankar, Telangana", type: "village", lat: 18.8167, lng: 79.9167, famous_for: "Shiva Temple & Project" },
          { name: "Medaram", address: "Medaram, Mulugu, Telangana", type: "village", lat: 18.1167, lng: 79.4833, famous_for: "Sammakka Saralamma Jatara" },
          { name: "Pochampally", address: "Pochampally, Yadadri, Telangana", type: "village", lat: 17.3500, lng: 78.9500, famous_for: "Ikat Handloom" },
          { name: "Kolanupaka", address: "Kolanupaka, Nalgonda, Telangana", type: "village", lat: 17.1167, lng: 79.0833, famous_for: "Jain Temple" },
          { name: "Vemulawada", address: "Vemulawada, Rajanna Sircilla, Telangana", type: "village", lat: 18.3167, lng: 78.8667, famous_for: "Raja Rajeshwara Temple" },
          { name: "Basara", address: "Basara, Nirmal, Telangana", type: "village", lat: 18.8333, lng: 77.9833, famous_for: "Saraswati Temple" }
        ],
        airports: [
          { name: "Rajiv Gandhi International Airport", address: "Shamshabad, Hyderabad, Telangana", type: "airport", lat: 17.2403, lng: 78.4294, code: "HYD" },
          { name: "Warangal Airport", address: "Mamnoor, Warangal, Telangana", type: "airport", lat: 17.9200, lng: 79.6000, code: "WGC" }
        ],
        transport: [
          { name: "Secunderabad Railway Station", address: "Secunderabad Junction, Telangana", type: "transport", lat: 17.4399, lng: 78.4983 },
          { name: "Hyderabad Deccan Station", address: "Nampally Station, Hyderabad, Telangana", type: "transport", lat: 17.3616, lng: 78.4747 },
          { name: "Kacheguda Railway Station", address: "Kacheguda, Hyderabad, Telangana", type: "transport", lat: 17.3850, lng: 78.4867 },
          { name: "Warangal Railway Station", address: "Warangal Junction, Telangana", type: "transport", lat: 17.9689, lng: 79.5941 }
        ],
        government: [
          { name: "Telangana Secretariat", address: "Secretariat, Hyderabad, Telangana", type: "government", lat: 17.3850, lng: 78.4867 },
          { name: "Telangana High Court", address: "High Court, Hyderabad, Telangana", type: "government", lat: 17.4126, lng: 78.4392 },
          { name: "Raj Bhavan Telangana", address: "Raj Bhavan, Hyderabad, Telangana", type: "government", lat: 17.4126, lng: 78.4392 }
        ],
        tech_hubs: [
          { name: "HITEC City", address: "HITEC City, Hyderabad, Telangana", type: "tech_hub", lat: 17.4435, lng: 78.3772 },
          { name: "Gachibowli", address: "Gachibowli, Hyderabad, Telangana", type: "tech_hub", lat: 17.4399, lng: 78.3482 },
          { name: "Madhapur", address: "Madhapur, Hyderabad, Telangana", type: "tech_hub", lat: 17.4474, lng: 78.3914 },
          { name: "Kondapur", address: "Kondapur, Hyderabad, Telangana", type: "tech_hub", lat: 17.4641, lng: 78.3648 }
        ]
      },

      // CHHATTISGARH STATE - Complete Database
      chhattisgarh: {
        tier1_cities: [
          { name: "Raipur", address: "Raipur, Chhattisgarh", type: "city", lat: 21.2514, lng: 81.6296, population: "1,010,087" },
          { name: "Bhilai", address: "Bhilai, Durg, Chhattisgarh", type: "city", lat: 21.1938, lng: 81.3509, population: "625,138" }
        ],
        tier2_cities: [
          { name: "Korba", address: "Korba, Chhattisgarh", type: "city", lat: 22.3595, lng: 82.7501, population: "365,073" },
          { name: "Bilaspur", address: "Bilaspur, Chhattisgarh", type: "city", lat: 22.0797, lng: 82.1391, population: "331,030" },
          { name: "Durg", address: "Durg, Chhattisgarh", type: "city", lat: 21.1901, lng: 81.2849, population: "268,806" },
          { name: "Rajnandgaon", address: "Rajnandgaon, Chhattisgarh", type: "city", lat: 21.0974, lng: 81.0379, population: "163,122" },
          { name: "Jagdalpur", address: "Jagdalpur, Bastar, Chhattisgarh", type: "city", lat: 19.0821, lng: 82.0323, population: "135,599" },
          { name: "Raigarh", address: "Raigarh, Chhattisgarh", type: "city", lat: 21.8974, lng: 83.3950, population: "130,014" }
        ],
        tier3_towns: [
          { name: "Ambikapur", address: "Ambikapur, Surguja, Chhattisgarh", type: "town", lat: 23.1186, lng: 83.1956, population: "114,468" },
          { name: "Mahasamund", address: "Mahasamund, Chhattisgarh", type: "town", lat: 21.1067, lng: 82.0988, population: "58,204" },
          { name: "Dhamtari", address: "Dhamtari, Chhattisgarh", type: "town", lat: 20.7081, lng: 81.5497, population: "84,177" },
          { name: "Kanker", address: "Kanker, Chhattisgarh", type: "town", lat: 20.2719, lng: 81.4929, population: "35,410" },
          { name: "Kawardha", address: "Kawardha, Kabirdham, Chhattisgarh", type: "town", lat: 22.0167, lng: 81.2333, population: "28,031" },
          { name: "Dongargarh", address: "Dongargarh, Rajnandgaon, Chhattisgarh", type: "town", lat: 21.1833, lng: 80.7500, population: "32,571" },
          { name: "Bemetara", address: "Bemetara, Chhattisgarh", type: "town", lat: 21.7167, lng: 81.5333, population: "26,758" },
          { name: "Mungeli", address: "Mungeli, Chhattisgarh", type: "town", lat: 22.0667, lng: 81.6833, population: "23,447" },
          { name: "Akaltara", address: "Akaltara, Janjgir-Champa, Chhattisgarh", type: "town", lat: 22.0167, lng: 82.4333, population: "25,750" },
          { name: "Baloda Bazar", address: "Baloda Bazar, Chhattisgarh", type: "town", lat: 21.6500, lng: 82.1667, population: "32,441" }
        ],
        villages: [
          { name: "Sirpur", address: "Sirpur, Mahasamund, Chhattisgarh", type: "village", lat: 21.2000, lng: 82.5500, famous_for: "Ancient Buddhist Site" },
          { name: "Chitrakote Falls", address: "Chitrakote, Bastar, Chhattisgarh", type: "village", lat: 19.1833, lng: 81.8333, famous_for: "Niagara of India" },
          { name: "Tirathgarh Falls", address: "Tirathgarh, Bastar, Chhattisgarh", type: "village", lat: 19.0167, lng: 81.9167, famous_for: "Waterfall" },
          { name: "Barnawapara", address: "Barnawapara, Mahasamund, Chhattisgarh", type: "village", lat: 21.2500, lng: 82.3333, famous_for: "Wildlife Sanctuary" },
          { name: "Kanger Valley", address: "Kanger Valley, Bastar, Chhattisgarh", type: "village", lat: 18.8667, lng: 81.9333, famous_for: "National Park" },
          { name: "Mainpat", address: "Mainpat, Surguja, Chhattisgarh", type: "village", lat: 23.4167, lng: 83.2000, famous_for: "Shimla of Chhattisgarh" },
          { name: "Ratanpur", address: "Ratanpur, Bilaspur, Chhattisgarh", type: "village", lat: 22.3000, lng: 82.1667, famous_for: "Ancient Capital" },
          { name: "Malhar", address: "Malhar, Bilaspur, Chhattisgarh", type: "village", lat: 21.8833, lng: 82.2833, famous_for: "Archaeological Site" },
          { name: "Bhoramdeo", address: "Bhoramdeo, Kawardha, Chhattisgarh", type: "village", lat: 22.1167, lng: 81.1000, famous_for: "Khajuraho of Chhattisgarh" },
          { name: "Tala", address: "Tala, Bilaspur, Chhattisgarh", type: "village", lat: 22.5833, lng: 82.7500, famous_for: "Achanakmar Tiger Reserve" }
        ],
        airports: [
          { name: "Swami Vivekananda Airport", address: "Mana, Raipur, Chhattisgarh", type: "airport", lat: 21.1804, lng: 81.7388, code: "RPR" },
          { name: "Bilaspur Airport", address: "Chakarbhatha, Bilaspur, Chhattisgarh", type: "airport", lat: 22.0833, lng: 82.1111, code: "PAB" }
        ],
        transport: [
          { name: "Raipur Railway Station", address: "Raipur Junction, Chhattisgarh", type: "transport", lat: 21.2514, lng: 81.6296 },
          { name: "Bilaspur Railway Station", address: "Bilaspur Junction, Chhattisgarh", type: "transport", lat: 22.0797, lng: 82.1391 },
          { name: "Durg Railway Station", address: "Durg Junction, Chhattisgarh", type: "transport", lat: 21.1901, lng: 81.2849 },
          { name: "Korba Railway Station", address: "Korba Junction, Chhattisgarh", type: "transport", lat: 22.3595, lng: 82.7501 }
        ],
        government: [
          { name: "Chhattisgarh Secretariat", address: "Mantralaya, Raipur, Chhattisgarh", type: "government", lat: 21.2514, lng: 81.6296 },
          { name: "Chhattisgarh High Court", address: "High Court, Bilaspur, Chhattisgarh", type: "government", lat: 22.0797, lng: 82.1391 },
          { name: "Raj Bhavan Chhattisgarh", address: "Raj Bhavan, Raipur, Chhattisgarh", type: "government", lat: 21.2514, lng: 81.6296 }
        ]
      },

      // Tier 2 Cities (Other States)
      tier2_cities: [
        { name: "Mysore", address: "Mysore, Karnataka", type: "city", lat: 12.2958, lng: 76.6394 },
        { name: "Mangalore", address: "Mangalore, Karnataka", type: "city", lat: 12.9141, lng: 74.8560 },
        { name: "Hubli", address: "Hubli, Karnataka", type: "city", lat: 15.3647, lng: 75.1240 },
        { name: "Belgaum", address: "Belgaum, Karnataka", type: "city", lat: 15.8497, lng: 74.4977 },
        { name: "Gulbarga", address: "Gulbarga, Karnataka", type: "city", lat: 17.3297, lng: 76.8343 },
        { name: "Davangere", address: "Davangere, Karnataka", type: "city", lat: 14.4644, lng: 75.9218 },
        { name: "Bellary", address: "Bellary, Karnataka", type: "city", lat: 15.1394, lng: 76.9214 },
        { name: "Bijapur", address: "Bijapur, Karnataka", type: "city", lat: 16.8302, lng: 75.7100 },
        { name: "Shimoga", address: "Shimoga, Karnataka", type: "city", lat: 13.9299, lng: 75.5681 },
        { name: "Tumkur", address: "Tumkur, Karnataka", type: "city", lat: 13.3379, lng: 77.1022 }
      ],

      // Tier 3 Cities & Towns
      tier3_towns: [
        { name: "Hassan", address: "Hassan, Karnataka", type: "town", lat: 13.0033, lng: 76.0965 },
        { name: "Mandya", address: "Mandya, Karnataka", type: "town", lat: 12.5214, lng: 76.8958 },
        { name: "Chikmagalur", address: "Chikmagalur, Karnataka", type: "town", lat: 13.3161, lng: 75.7720 },
        { name: "Udupi", address: "Udupi, Karnataka", type: "town", lat: 13.3409, lng: 74.7421 },
        { name: "Karwar", address: "Karwar, Karnataka", type: "town", lat: 14.8142, lng: 74.1297 },
        { name: "Raichur", address: "Raichur, Karnataka", type: "town", lat: 16.2120, lng: 77.3439 },
        { name: "Kolar", address: "Kolar, Karnataka", type: "town", lat: 13.1358, lng: 78.1298 },
        { name: "Chitradurga", address: "Chitradurga, Karnataka", type: "town", lat: 14.2251, lng: 76.3958 },
        { name: "Bagalkot", address: "Bagalkot, Karnataka", type: "town", lat: 16.1875, lng: 75.6972 },
        { name: "Gadag", address: "Gadag, Karnataka", type: "town", lat: 15.4167, lng: 75.6167 }
      ],

      // Villages & Small Towns
      villages: [
        { name: "Nandi Hills", address: "Nandi Hills, Chikkaballapur, Karnataka", type: "village", lat: 13.3703, lng: 77.6837 },
        { name: "Bannerghatta", address: "Bannerghatta, Bangalore Rural, Karnataka", type: "village", lat: 12.7993, lng: 77.5769 },
        { name: "Devanahalli", address: "Devanahalli, Bangalore Rural, Karnataka", type: "village", lat: 13.2429, lng: 77.7085 },
        { name: "Ramanagara", address: "Ramanagara, Karnataka", type: "village", lat: 12.7179, lng: 77.2823 },
        { name: "Channapatna", address: "Channapatna, Ramanagara, Karnataka", type: "village", lat: 12.6518, lng: 77.2068 },
        { name: "Doddaballapur", address: "Doddaballapur, Bangalore Rural, Karnataka", type: "village", lat: 13.2218, lng: 77.5348 },
        { name: "Hoskote", address: "Hoskote, Bangalore Rural, Karnataka", type: "village", lat: 13.0683, lng: 77.7983 },
        { name: "Nelamangala", address: "Nelamangala, Bangalore Rural, Karnataka", type: "village", lat: 13.1022, lng: 77.3932 },
        { name: "Anekal", address: "Anekal, Bangalore Urban, Karnataka", type: "village", lat: 12.7081, lng: 77.6953 },
        { name: "Magadi", address: "Magadi, Ramanagara, Karnataka", type: "village", lat: 12.9579, lng: 77.2265 }
      ],

      // Other Major Cities for Reference
      mumbai: [
        { name: "Chhatrapati Shivaji Airport", address: "Mumbai Airport, Maharashtra", type: "airport", lat: 19.0896, lng: 72.8656 },
        { name: "Gateway of India", address: "Gateway of India, Mumbai, Maharashtra", type: "landmark", lat: 18.9220, lng: 72.8347 },
        { name: "Marine Drive", address: "Marine Drive, Mumbai, Maharashtra", type: "landmark", lat: 18.9435, lng: 72.8234 },
        { name: "Bandra-Kurla Complex", address: "BKC, Mumbai, Maharashtra", type: "business", lat: 19.0596, lng: 72.8656 },
        { name: "Andheri", address: "Andheri, Mumbai, Maharashtra", type: "commercial", lat: 19.1136, lng: 72.8697 }
      ],

      delhi: [
        { name: "Indira Gandhi International Airport", address: "IGI Airport, Delhi", type: "airport", lat: 28.5562, lng: 77.1000 },
        { name: "India Gate", address: "India Gate, New Delhi", type: "landmark", lat: 28.6129, lng: 77.2295 },
        { name: "Red Fort", address: "Red Fort, Delhi", type: "landmark", lat: 28.6562, lng: 77.2410 },
        { name: "Connaught Place", address: "CP, New Delhi", type: "commercial", lat: 28.6315, lng: 77.2167 },
        { name: "Gurgaon Cyber City", address: "Cyber City, Gurgaon, Haryana", type: "tech_hub", lat: 28.4595, lng: 77.0266 }
      ]
    };
  }

  /**
   * Get current location using browser geolocation with Indian location focus
   */
  async getCurrentLocation() {
    // Check cache first
    if (this.currentLocationCache &&
        this.currentLocationTimestamp &&
        (Date.now() - this.currentLocationTimestamp) < this.cacheTimeout) {
      return this.currentLocationCache;
    }

    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        // Fallback to approximate location based on timezone/IP
        this.getApproximateIndianLocation().then(resolve).catch(reject);
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;

          // Validate if coordinates are within India bounds
          if (!this.isWithinIndiaBounds(latitude, longitude)) {
            console.warn('GPS coordinates outside India, using fallback location');
            try {
              const fallbackLocation = await this.getApproximateIndianLocation();
              resolve(fallbackLocation);
              return;
            } catch (fallbackError) {
              // Continue with original coordinates if fallback fails
            }
          }

          try {
            // Reverse geocode to get address with India focus
            const address = await this.reverseGeocodeIndia(latitude, longitude);

            const location = {
              latitude,
              longitude,
              address: address || `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`,
              accuracy: position.coords.accuracy,
              timestamp: new Date().toISOString(),
              source: 'gps'
            };

            // Cache the result
            this.currentLocationCache = location;
            this.currentLocationTimestamp = Date.now();

            resolve(location);
          } catch (error) {
            // If reverse geocoding fails, still return coordinates
            const location = {
              latitude,
              longitude,
              address: `Lat: ${latitude.toFixed(4)}, Lng: ${longitude.toFixed(4)}`,
              accuracy: position.coords.accuracy,
              timestamp: new Date().toISOString(),
              source: 'gps'
            };
            resolve(location);
          }
        },
        async (error) => {
          console.warn('GPS location failed:', error.message);
          // Fallback to approximate Indian location
          try {
            const fallbackLocation = await this.getApproximateIndianLocation();
            resolve(fallbackLocation);
          } catch (fallbackError) {
            reject(new Error(`Location access failed: ${error.message}`));
          }
        },
        {
          enableHighAccuracy: true,
          timeout: 15000, // Increased timeout
          maximumAge: 60000 // 1 minute cache
        }
      );
    });
  }

  /**
   * Check if coordinates are within India bounds
   */
  isWithinIndiaBounds(lat, lng) {
    // India bounding box (approximate)
    const INDIA_BOUNDS = {
      north: 37.6,
      south: 6.4,
      east: 97.25,
      west: 68.7
    };

    return lat >= INDIA_BOUNDS.south && lat <= INDIA_BOUNDS.north &&
           lng >= INDIA_BOUNDS.west && lng <= INDIA_BOUNDS.east;
  }

  /**
   * Get approximate Indian location as fallback
   */
  async getApproximateIndianLocation() {
    // Default to Bangalore (HAL headquarters) as fallback
    const defaultLocation = {
      latitude: 12.9716,
      longitude: 77.5946,
      address: "Bangalore, Karnataka, India (Approximate)",
      accuracy: 10000, // Low accuracy indicator
      timestamp: new Date().toISOString(),
      source: 'fallback'
    };

    try {
      // Try to get a better approximation based on timezone
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

      if (timezone.includes('Kolkata') || timezone.includes('Asia/Calcutta')) {
        // User is likely in India
        return defaultLocation;
      }

      // For demo purposes, return Bangalore location
      return defaultLocation;
    } catch (error) {
      return defaultLocation;
    }
  }

  /**
   * Reverse geocode with India focus
   */
  async reverseGeocodeIndia(latitude, longitude) {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1&countrycodes=in`
      );

      if (!response.ok) {
        throw new Error('Reverse geocoding request failed');
      }

      const result = await response.json();

      if (result && result.display_name) {
        // Format address for Indian context
        const address = result.display_name;
        return address;
      }

      return null;
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      return null;
    }
  }

  /**
   * Search for locations based on query
   */
  async searchLocations(query, limit = 10) {
    if (!query || query.length < 2) {
      return this.getPopularLocations().bangalore.slice(0, limit);
    }

    // Check cache
    const cacheKey = `search_${query.toLowerCase()}`;
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.results;
      }
    }

    try {
      // Search in popular locations first
      const popularResults = this.searchInPopularLocations(query);
      
      // If we have enough results from popular locations, return them
      if (popularResults.length >= limit) {
        const results = popularResults.slice(0, limit);
        this.cache.set(cacheKey, { results, timestamp: Date.now() });
        return results;
      }

      // Otherwise, try to geocode the query
      const geocodeResults = await this.geocodeLocation(query);
      const combinedResults = [...popularResults, ...geocodeResults].slice(0, limit);
      
      this.cache.set(cacheKey, { results: combinedResults, timestamp: Date.now() });
      return combinedResults;
      
    } catch (error) {
      console.error('Location search error:', error);
      // Return popular locations as fallback
      return this.getPopularLocations().bangalore.slice(0, limit);
    }
  }

  /**
   * Search in comprehensive Indian locations database
   */
  searchInPopularLocations(query) {
    const locations = this.getPopularLocations();
    const allLocations = [
      // Odisha
      ...locations.odisha.tier1_cities,
      ...locations.odisha.tier2_cities,
      ...locations.odisha.tier3_towns,
      ...locations.odisha.villages,
      ...locations.odisha.airports,
      ...locations.odisha.transport,
      ...locations.odisha.government,

      // Andhra Pradesh
      ...locations.andhra_pradesh.tier1_cities,
      ...locations.andhra_pradesh.tier2_cities,
      ...locations.andhra_pradesh.tier3_towns,
      ...locations.andhra_pradesh.villages,
      ...locations.andhra_pradesh.airports,

      // Telangana
      ...locations.telangana.tier1_cities,
      ...locations.telangana.tier2_cities,
      ...locations.telangana.tier3_towns,
      ...locations.telangana.villages,
      ...locations.telangana.airports,
      ...locations.telangana.transport,
      ...locations.telangana.government,
      ...locations.telangana.tech_hubs,

      // Chhattisgarh
      ...locations.chhattisgarh.tier1_cities,
      ...locations.chhattisgarh.tier2_cities,
      ...locations.chhattisgarh.tier3_towns,
      ...locations.chhattisgarh.villages,
      ...locations.chhattisgarh.airports,
      ...locations.chhattisgarh.transport,
      ...locations.chhattisgarh.government,

      // Karnataka (Enhanced)
      ...locations.karnataka.tier1_cities,
      ...locations.karnataka.bangalore_areas,

      // Other states
      ...locations.tier2_cities,
      ...locations.tier3_towns,
      ...locations.villages,
      ...locations.mumbai,
      ...locations.delhi
    ];

    const queryLower = query.toLowerCase();
    
    return allLocations.filter(location => 
      location.name.toLowerCase().includes(queryLower) ||
      location.address.toLowerCase().includes(queryLower)
    ).map(location => ({
      ...location,
      score: this.calculateRelevanceScore(location, queryLower)
    })).sort((a, b) => b.score - a.score);
  }

  /**
   * Calculate relevance score for search results
   */
  calculateRelevanceScore(location, query) {
    let score = 0;
    
    // Exact name match gets highest score
    if (location.name.toLowerCase() === query) {
      score += 100;
    } else if (location.name.toLowerCase().startsWith(query)) {
      score += 80;
    } else if (location.name.toLowerCase().includes(query)) {
      score += 60;
    }
    
    // Address match
    if (location.address.toLowerCase().includes(query)) {
      score += 40;
    }
    
    // Enhanced type-based scoring with state priorities
    const typeScores = {
      office: 25,
      airport: 20,
      transport: 18,
      tech_hub: 15,
      city: 15,
      commercial: 12,
      government: 10,
      town: 8,
      village: 6,
      shopping: 5,
      landmark: 5,
      residential: 4,
      business: 4,
      park: 3
    };

    // State-based bonus scoring
    const address = location.address.toLowerCase();
    if (address.includes('odisha') || address.includes('orissa')) {
      score += 15; // Priority for Odisha
    } else if (address.includes('andhra pradesh')) {
      score += 15; // Priority for Andhra Pradesh
    } else if (address.includes('telangana')) {
      score += 15; // Priority for Telangana
    } else if (address.includes('chhattisgarh')) {
      score += 15; // Priority for Chhattisgarh
    } else if (address.includes('karnataka')) {
      score += 10; // Karnataka bonus
    }
    
    score += typeScores[location.type] || 0;
    
    return score;
  }

  /**
   * Geocode location using Nominatim with comprehensive India focus
   */
  async geocodeLocation(query) {
    try {
      // Try multiple search strategies for better results
      const searchQueries = [
        `${query}, Odisha, India`,
        `${query}, Andhra Pradesh, India`,
        `${query}, Telangana, India`,
        `${query}, Chhattisgarh, India`,
        `${query}, Karnataka, India`,
        `${query}, India`
      ];

      let allResults = [];

      for (const searchQuery of searchQueries) {
        const encodedQuery = encodeURIComponent(searchQuery);
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodedQuery}&limit=3&countrycodes=in&bounded=1&viewbox=68.7,37.6,97.25,6.4`
        );

        if (response.ok) {
          const results = await response.json();
          if (results && results.length > 0) {
            allResults.push(...results);
          }
        }

        // Break early if we have enough results
        if (allResults.length >= 8) break;
      }

      // Remove duplicates and format results
      const uniqueResults = [];
      const seenLocations = new Set();

      for (const result of allResults) {
        const locationKey = `${result.lat},${result.lon}`;
        if (!seenLocations.has(locationKey)) {
          seenLocations.add(locationKey);

          // Determine location type based on address
          let locationType = 'geocoded';
          const address = result.display_name.toLowerCase();

          if (address.includes('village')) locationType = 'village';
          else if (address.includes('town')) locationType = 'town';
          else if (address.includes('city')) locationType = 'city';
          else if (address.includes('airport')) locationType = 'airport';
          else if (address.includes('railway') || address.includes('station')) locationType = 'transport';
          else if (address.includes('government') || address.includes('secretariat')) locationType = 'government';

          uniqueResults.push({
            name: result.display_name.split(',')[0],
            address: result.display_name,
            latitude: parseFloat(result.lat),
            longitude: parseFloat(result.lon),
            type: locationType,
            score: 30 // Lower score than popular locations
          });
        }
      }

      return uniqueResults.slice(0, 8); // Return top 8 results

    } catch (error) {
      console.error('Geocoding error:', error);
      return [];
    }
  }

  /**
   * Reverse geocode coordinates to address
   */
  async reverseGeocode(latitude, longitude) {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`
      );
      
      if (!response.ok) {
        throw new Error('Reverse geocoding request failed');
      }
      
      const result = await response.json();
      return result.display_name;
      
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      return null;
    }
  }

  /**
   * Get distance between two points (Haversine formula)
   */
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Convert degrees to radians
   */
  toRadians(degrees) {
    return degrees * (Math.PI / 180);
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    this.currentLocationCache = null;
    this.currentLocationTimestamp = null;
  }
}

// Create singleton instance
const locationService = new LocationService();

export default locationService;
