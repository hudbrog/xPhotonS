import photon_reader

pr = photon_reader.PhotonReader("10mm-benchy.photon")
pr.read_data()
pr.print_header()