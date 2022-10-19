# STM32-Based Smart Domestic Terminal System

## Graduation Project

## Abstract

Domestic terminals are newly invented home automation devices combining technology from multiple areas of information science. While they are receiving increasing attention of developers and customers, certain problems discovered in traditional designs including limited control range, difficulty in planting, lack of support for multiple-user situations and low compatibility still hinder the application value and potential market of domestic terminals. Therefore, this article proposes a smart domestic terminal system based on STM32, which consists of embedded device, server and WeChat Miniprogram, improving the flexibility, user-friendliness and portability of the product, while allowing for rich scalability to larger system in future development.

This article firstly analyses the existing problems in present products, designs the system and module structures as well as the communication interface specifications. The project chooses STM32F407 as the micro-controller, correspondingly selecting OV2640 camera and DHT11 temperature and humidity sensor. Then, μC/OS-II operating system and lwIP TCP/IP Stack are transported to STM32, which are used as basic environments for the development of functions including sensor-data capturing and internet transmission. Flask framework is used by the server for Web services and a Socket server module is designed, realizing user-device management and data transfer. WeChat Miniprogram is developed for user login, registration and data interaction. Lastly, the article presents module tests and system integration test results, concluding that the sub-systems all function as anticipated and is able to coordinate correctly. The users are allowed to login and bind their devices so as to request collected data and control their devices.

## Description

There are 3 subsystems in this project. 
- Embedded device: STM32
- Interactive application: WeChat Miniprogram
- Server: Flask with WebSocket

## References

[1] Lu li,Changkun wang,Fuqiang zhao. A Smart Home Control System Integrated the Improved Streaming Media Technology and Raspberry Pi[C]//Proceedings of 2015 Ssr International Conference on Social Sciences and Information(ssr-ssi 2015 V11),  Singapore Management and Sports Science Institute, 2015: 656-659.
[2] Zhang ya'nan,Xiao guijin,Xu jiansheng. The Wireless Image Transmission System of Capsule Endoscope Based on Stm32f103[C]//Proceedings of 2016 2nd International Conference on Mechanical,electronic and Information Technology Engineering(icmite 2016),  Destech Publications, 2016: 309-315.
[3] Deshun fan,Jichun zhao. The Design of Image Transmission System Based on Stm32f429zi[C]//Proceedings of 2017 4th International Conference on Machinery,materials and Computer(macmc 2017),  Atlantis Press, 2017: 256-260.
[4] Zheng liu,Gang du,Wenhui zhuang, et al. Design of Camera Type Handling Trolley Based on Stm32[C]//Proceedings of 2019 3rd International Conference on Computer Engineering,information Science and Internet Technology(cii 2019),  Clausius Scientific Press,canada, 2019: 145-150.
[5] Ghoraani behnaz,Galvin james e.,Jimenez-shahed joohi. Point of View: Wearable Systems for At-home Monitoring of Motor Complications in Parkinson's Disease Should Deliver Clinically Actionable Information[J]. Parkinsonism and Related Disorders, 2021, 84: .
[6] Wang ju,Spicher nicolai,Warnecke joana m., et al. Unobtrusive Health Monitoring in Private Spaces: the Smart Home[J]. Sensors, 2021, 21(3): .
[7] Evaluation of the Effectiveness, Implementation and Cost-effectiveness of the Stay One Step Ahead Home Safety Promotion Intervention for Pre-school Children: a Study Protocol.[J]. Injury Prevention : Journal of the International Society for Child and Adolescent Injury Prevention, 2020, 26(6): .
[8] Evan r. polzer ma,Kathryn nearing phd M,Christopher e. knoepke msw P, et al. “safety in Dementia”: Development of an Online Caregiver Tool for Firearm, Driving, and Home Safety[J]. Journal of the American Geriatrics Society, 2020, 68(9): .
[9] Ghorayeb abir,Comber rob,Gooberman hill rachael. Older Adults' Perspectives of Smart Home Technology: Are We Developing the Technology That Older People Want?[J]. International Journal of Human-computer Studies, 2021, 147: .

