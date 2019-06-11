//
//  ViewController.swift
//  LineCalculator
//
//  Created by Derek Roy on 2019-05-21.
//  Copyright © 2019 IBM. All rights reserved.
//

import UIKit

class ViewController: UIViewController, UIImagePickerControllerDelegate,UINavigationControllerDelegate, URLSessionDelegate, URLSessionTaskDelegate, URLSessionDataDelegate {
    
    @IBOutlet weak var Camera: UIButton!
    @IBOutlet weak var Picture: UIImageView!
    @IBOutlet weak var People: UILabel!
    @IBOutlet weak var Last: UILabel!
    let url = URL(string: "http://drv-ctp6.canlab.ibm.com:5000/data")!
    var timer = Timer()

    override func viewDidLoad() {
        self.setValues()
        self.timeit()
        super.viewDidLoad()
    }
    

    @IBAction func CameraButton(_ sender: UIButton) {
        let image = UIImagePickerController()
        image.delegate = self
        image.sourceType = UIImagePickerController.SourceType.camera
        image.allowsEditing = false
        self.present(image, animated:true){
            //Complete
        }
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        if let image = info[UIImagePickerController.InfoKey.originalImage] as? UIImage{
            Picture.image = image
            uploadImage(image:image)
        }
        self.dismiss(animated: true, completion: nil)
    }
    
    func uploadImage(image:UIImage){
        
        let imageData:Data = image.jpegData(compressionQuality: 1.0)!
        let filename = "line.png"

        // generate boundary string using a unique per-app string
        let boundary = UUID().uuidString

        let fieldName = "reqtype"
        let fieldValue = "fileupload"

        let fieldName2 = "userhash"
        let fieldValue2 = "caa3dce4fcb36cfdf9258ad9c"

        let config = URLSessionConfiguration.default
        let session = URLSession(configuration: config)

        // Set the URLRequest to POST and to the specified URL
        var urlRequest = URLRequest(url: URL(string: "http://drv-ctp6.canlab.ibm.com:5000/data")!)
        urlRequest.httpMethod = "POST"

        // Set Content-Type Header to multipart/form-data, this is equivalent to submitting form data with file upload in a web browser
        // And the boundary is also set here
        urlRequest.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var data = Data()

        // Add the reqtype field and its value to the raw http request data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"\(fieldName)\"\r\n\r\n".data(using: .utf8)!)
        data.append("\(fieldValue)".data(using: .utf8)!)

        // Add the userhash field and its value to the raw http reqyest data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"\(fieldName2)\"\r\n\r\n".data(using: .utf8)!)
        data.append("\(fieldValue2)".data(using: .utf8)!)

        // Add the image data to the raw http request data
        data.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"fileToUpload\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        data.append("Content-Type: String\r\n\r\n".data(using: .utf8)!)
        data.append(imageData)

        // End the raw http request data, note that there is 2 extra dash ("-") at the end, this is to indicate the end of the data
        // According to the HTTP 1.1 specification https://tools.ietf.org/html/rfc7230
        data.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        // Send a POST request to the URL, with the data we created earlier
        session.uploadTask(with: urlRequest, from: data, completionHandler: { responseData, response, error in

            if(error != nil){
                print("\(error!.localizedDescription)")
            }

            guard let responseData = responseData else {
                print("no response data")
                return
            }

            if let responseString = String(data: responseData, encoding: .utf8) {
                print("uploaded to: \(responseString)")
            }
        }).resume()
        
    }
    
    @objc func setValues(){
        let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
            guard let data = data else { return }
            let x = String(data: data, encoding: .utf8)!
            self.process(s:x)
        }
        task.resume()
    }
    
    func timeit(){
        timer = Timer.scheduledTimer(timeInterval: 10, target: self, selector: #selector(update(timer:)), userInfo: nil, repeats: true)
    }
    
    @objc func update(timer:Timer){
        let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
            guard let data = data else { return }
            let x = String(data: data, encoding: .utf8)!
            self.process(s:x)
        }
        task.resume()
    }
    
    func process(s:String){
        var out = s.split(separator: ",")
        People.text = String(out[0].dropFirst(1))
        Last.text = String(out[1].dropLast(2))
    }
}
